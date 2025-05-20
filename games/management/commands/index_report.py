# games/management/commands/index_report.py
import os  # manejar rutas y sistema de ficheros
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.db.utils import DataError, IntegrityError


class Command(BaseCommand):
    """
    Comando que genera un informe sobre el rendimiento y tamaño de índices
    para la columna `app_id` en la tabla `games_game`, comparando:
      - B-tree sin índice
      - Creación y uso de índice B-tree
      - Creación y uso de índice Hash (si PostgreSQL lo permite)
    Además mide el tamaño en disco de los índices y la tabla.
    """

    help = (
        "Genera un informe de EXPLAIN ANALYZE y pg_relation_size sobre `app_id`, "
        "incluyendo opciones B-tree y Hash."
    )

    def add_arguments(self, parser):
        # Definimos un argumento obligatorio --app-id para la consulta de ejemplo
        parser.add_argument(
            "--app-id",
            dest="app_id",
            required=True,
            help="ID de aplicación (app_id) para filtrar la consulta",
        )

    def run_explain(self, sql, params=None):
        """
        Ejecuta un EXPLAIN ANALYZE con la sentencia SQL proporcionada.
        Devuelve una lista de líneas del plan de ejecución.
        """
        with connection.cursor() as cursor:
            # Ejecuta la consulta parametrizada para seguridad
            cursor.execute(sql, params or [])
            # Recoge cada fila como una línea del plan
            return [row[0] for row in cursor.fetchall()]

    def get_size_pretty(self, relation):
        """
        Usa pg_relation_size para obtener el tamaño legible en disco
        de una tabla o índice (relation).
        """
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT pg_size_pretty(pg_relation_size('{relation}'));")
            # Devuelve el valor formateado (por ejemplo '2472 kB')
            return cursor.fetchone()[0]

    def handle(self, *args, **options):
        # Capturamos el parámetro --app-id
        app_id = options["app_id"]
        # Nombre de la tabla y de los índices a usar
        table = "games_game"
        idx_btree = "idx_games_game_app_id"
        idx_hash = "idx_games_game_app_id_hash"

        # Directorio donde guardaremos los informes
        report_dir = os.path.join(os.getcwd(), "reports")
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, f"report_appid_{app_id}.md")

        # Lista que almacenará cada línea del Markdown
        lines = []
        # Sentencia genérica para EXPLAIN ANALYZE
        explain_sql = f"EXPLAIN ANALYZE SELECT * FROM {table} WHERE app_id = %s;"

        # --------------------------------------------------------------------
        # 1) B-tree: sin índice
        # --------------------------------------------------------------------
        # Eliminamos el índice B-tree si existe
        with transaction.atomic():
            connection.cursor().execute(f"DROP INDEX IF EXISTS {idx_btree};")
        lines.append("## 1. B-tree sin índice")
        # Ejecutamos EXPLAIN ANALYZE y guardamos el plan
        plan = self.run_explain(explain_sql, [app_id])
        lines.append("```")
        lines.extend(plan)
        lines.append("```")

        # --------------------------------------------------------------------
        # 2) B-tree: creación de índice y consulta
        # --------------------------------------------------------------------
        # Añadimos sección para mostrar la creación del índice
        lines.append("## 2. Creación índice B-tree")
        lines.append("```")
        lines.append(f"CREATE INDEX {idx_btree} ON {table}(app_id);")
        lines.append("```")
        # Creamos realmente el índice si no existe
        with transaction.atomic():
            connection.cursor().execute(
                f"CREATE INDEX IF NOT EXISTS {idx_btree} ON {table}(app_id);"
            )
        # Consulta con índice B-tree
        lines.append("### Consulta con índice B-tree")
        plan = self.run_explain(explain_sql, [app_id])
        lines.append("```")
        lines.extend(plan)
        lines.append("```")

        # --------------------------------------------------------------------
        # 3) Dimensionamiento B-tree
        # --------------------------------------------------------------------
        lines.append("## 3. Dimensionamiento B-tree")
        size_table = self.get_size_pretty(table)
        size_btree = self.get_size_pretty(idx_btree)
        lines.append(f"- Tamaño tabla `{table}`: {size_table}")
        lines.append(f"- Tamaño índice B-tree `{idx_btree}`: {size_btree}")

        # --------------------------------------------------------------------
        # 4) Hash: eliminar B-tree, crear índice Hash y consulta
        # --------------------------------------------------------------------
        # Borramos el B-tree para probar Hash
        with transaction.atomic():
            connection.cursor().execute(f"DROP INDEX IF EXISTS {idx_btree};")
        lines.append("## 4. Índice Hash")
        # Mostrar creación índice Hash
        lines.append("### Creación índice Hash")
        lines.append("```")
        lines.append(f"CREATE INDEX {idx_hash} ON {table} USING HASH (app_id);")
        lines.append("```")
        # Intentamos crear el índice Hash, atrapando excepciones
        try:
            with transaction.atomic():
                connection.cursor().execute(
                    f"CREATE INDEX IF NOT EXISTS {idx_hash} ON {table} USING HASH (app_id);"
                )
        except Exception as e:
            lines.append(f"_Hash no soportado: {e}_")

        # Consulta con índice Hash
        lines.append("### Consulta con índice Hash")
        try:
            plan = self.run_explain(explain_sql, [app_id])
            lines.append("```")
            lines.extend(plan)
            lines.append("```")
        except Exception:
            lines.append("_No se pudo ejecutar EXPLAIN con hash_")

        # --------------------------------------------------------------------
        # 5) Dimensionamiento Hash
        # --------------------------------------------------------------------
        lines.append("## 5. Dimensionamiento Hash")
        try:
            size_hash = self.get_size_pretty(idx_hash)
            lines.append(f"- Tamaño índice Hash `{idx_hash}`: {size_hash}")
        except Exception:
            lines.append("_No disponible tamaño índice Hash_")

        # --------------------------------------------------------------------
        # 6) Conclusiones y recomendaciones
        # --------------------------------------------------------------------
        lines.append("## 6. Conclusiones y recomendaciones")

        # Escribimos el informe completo en un fichero Markdown
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# Informe de Índices para app_id {app_id}\n\n")
            f.write("\n".join(lines))

        # Mensaje final por consola
        self.stdout.write(f"Reporte guardado en {report_path}")
