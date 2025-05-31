import os  # manejar rutas y sistema de ficheros
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.db.utils import DataError, IntegrityError


class Command(BaseCommand):
    """
    Comando que genera un informe sobre el rendimiento y tamaño de índices
    para la columna `price` en la tabla `games_game`, comparando:
      - B-tree sin índice
      - Creación y uso de índice B-tree
      - Creación y uso de índice Hash (si PostgreSQL lo permite)
    Además mide el tamaño en disco de los índices y la tabla.
    """

    help = (
        "Genera un informe de EXPLAIN ANALYZE y pg_relation_size sobre `price`, "
        "incluyendo opciones B-tree y Hash."
    )

    def add_arguments(self, parser):
        # Definimos dos argumentos obligatorios para rangos de precio
        parser.add_argument(
            "--price-1",
            dest="price_1",
            required=True,
            help="Límite inferior del rango de precios (ej. 0)",
        )
        parser.add_argument(
            "--price-2",
            dest="price_2",
            required=True,
            help="Límite superior del rango de precios (ej. 50)",
        )

    def run_explain(self, sql, params=None):
        """
        Ejecuta un EXPLAIN ANALYZE con la sentencia SQL proporcionada.
        Devuelve una lista de líneas del plan de ejecución.
        """
        with connection.cursor() as cursor:
            cursor.execute(sql, params or [])
            return [row[0] for row in cursor.fetchall()]

    def get_size_pretty(self, relation):
        """
        Usa pg_relation_size para obtener el tamaño legible en disco
        de una tabla o índice (relation).
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_size_pretty(pg_relation_size(%s));", [relation])
            return cursor.fetchone()[0]

    def handle(self, *args, **options):
        # Capturamos los parámetros --price-1 y --price-2
        price_1 = options["price_1"]
        price_2 = options["price_2"]

        # Definición de nombres
        table = "games_game"
        idx_btree = "idx_games_game_price"
        idx_hash = "idx_games_game_price_hash"

        # Directorio donde guardaremos los informes
        report_dir = os.path.join(os.getcwd(), "reports")
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(
            report_dir, f"report_prices_{price_1}_to_{price_2}.md"
        )

        # Sentencia genérica para EXPLAIN ANALYZE solo con price
        explain_sql = (
            f"EXPLAIN ANALYZE SELECT * FROM {table} "
            f"WHERE {table}.price BETWEEN %s AND %s;"
        )

        lines = []

        # --------------------------------------------------------------------
        # 1) B-tree: sin índice
        # --------------------------------------------------------------------
        with transaction.atomic():
            connection.cursor().execute(f"DROP INDEX IF EXISTS {idx_btree};")
        lines.append("## 1. B-tree sin índice")
        plan = self.run_explain(explain_sql, [price_1, price_2])
        lines.append("```")
        lines.extend(plan)
        lines.append("```")

        # --------------------------------------------------------------------
        # 2) B-tree: creación de índice y consulta
        # --------------------------------------------------------------------
        lines.append("## 2. Creación índice B-tree")
        lines.append("```")
        lines.append(f"CREATE INDEX {idx_btree} ON {table}(price);")
        lines.append("```")
        with transaction.atomic():
            connection.cursor().execute(
                f"CREATE INDEX IF NOT EXISTS {idx_btree} ON {table}(price);"
            )
        lines.append("### Consulta con índice B-tree")
        plan = self.run_explain(explain_sql, [price_1, price_2])
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
        with transaction.atomic():
            connection.cursor().execute(f"DROP INDEX IF EXISTS {idx_btree};")
        lines.append("## 4. Índice Hash")
        lines.append("### Creación índice Hash")
        lines.append("```")
        lines.append(f"CREATE INDEX {idx_hash} ON {table} USING HASH (price);")
        lines.append("```")
        try:
            with transaction.atomic():
                connection.cursor().execute(
                    f"CREATE INDEX IF NOT EXISTS {idx_hash} ON {table} USING HASH (price);"
                )
        except Exception as e:
            lines.append(f"_Hash no soportado: {e}_")

        lines.append("### Consulta con índice Hash")
        try:
            plan = self.run_explain(explain_sql, [price_1, price_2])
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
            f.write(
                f"# Informe de Índices para price BETWEEN {price_1} y {price_2}\n\n"
            )
            f.write("\n".join(lines))

        self.stdout.write(f"Reporte guardado en {report_path}")
