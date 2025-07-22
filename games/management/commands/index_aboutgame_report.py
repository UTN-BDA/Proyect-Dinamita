import os
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = "Genera un informe de rendimiento de búsqueda por about_game"

    def add_arguments(self, parser):
        parser.add_argument(
            "--about", required=True, help="Texto exacto del campo about_game"
        )

    def run_explain(self, sql, params=None):
        with connection.cursor() as cursor:
            cursor.execute(sql, params or [])
            return [row[0] for row in cursor.fetchall()]

    def get_size_pretty(self, relation):
        with connection.cursor() as cursor:
            # SEGURIDAD: Usar parámetros en lugar de f-strings
            cursor.execute("SELECT pg_size_pretty(pg_relation_size(%s));", [relation])
            return cursor.fetchone()[0]

    def handle(self, *args, **options):
        about = options["about"]
        table = "games_game"
        idx_btree = "idx_game_about_btree"
        idx_hash = "idx_game_about_hash"

        # Crear la carpeta para reportes si no existe
        report_dir = os.path.join(os.getcwd(), "reports")
        os.makedirs(report_dir, exist_ok=True)
        path = os.path.join(
            report_dir, f"report_about_{about[:20].replace(' ', '_')}.md"
        )
        lines = []

        explain_sql = f"EXPLAIN ANALYZE SELECT * FROM {table} WHERE about_game = %s;"

        # 1. Sin índice B-tree
        with transaction.atomic():
            connection.cursor().execute(f"DROP INDEX IF EXISTS {idx_btree};")
        lines.append("## 1. Sin índice B-tree")
        lines.append("```")
        lines.extend(self.run_explain(explain_sql, [about]))
        lines.append("```")

        # 2. Con índice B-tree
        with transaction.atomic():
            try:
                connection.cursor().execute(
                    f"CREATE INDEX IF NOT EXISTS {idx_btree} ON {table}(about_game);"
                )
                lines.append("## 2. Con índice B-tree")
                lines.append("```")
                lines.extend(self.run_explain(explain_sql, [about]))
                lines.append("```")
                lines.append("## 3. Tamaño índice B-tree")
                lines.append(f"- Tabla `{table}`: {self.get_size_pretty(table)}")
                lines.append(
                    f"- Índice `{idx_btree}`: {self.get_size_pretty(idx_btree)}"
                )
            except OperationalError as e:
                if "index row size" in str(e):
                    lines.append(
                        f"_No se pudo crear el índice B-tree debido al tamaño del campo: {str(e)}_"
                    )
                else:
                    lines.append(f"_Error al crear el índice B-tree: {str(e)}_")

        # 3. Eliminar índice B-tree y crear índice Hash
        with transaction.atomic():
            connection.cursor().execute(f"DROP INDEX IF EXISTS {idx_btree};")
        try:
            with transaction.atomic():
                connection.cursor().execute(
                    f"CREATE INDEX IF NOT EXISTS {idx_hash} ON {table} USING HASH (about_game);"
                )
            lines.append("## 4. Índice Hash")
            lines.append("```")
            lines.extend(self.run_explain(explain_sql, [about]))
            lines.append("```")
            lines.append(f"- Índice `{idx_hash}`: {self.get_size_pretty(idx_hash)}")
        except Exception as e:
            lines.append(f"_Hash no soportado: {e}_")

        # Guardamos el reporte en un archivo .md
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# Reporte búsqueda por about_game = '{about}'\n\n")
            f.write("\n".join(lines))

        self.stdout.write(f"Reporte guardado en {path}")
