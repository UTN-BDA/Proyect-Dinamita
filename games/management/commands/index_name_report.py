import os
from django.core.management.base import BaseCommand
from django.db import connection, transaction


class Command(BaseCommand):
    help = "Genera un informe de rendimiento de búsqueda por name"

    def add_arguments(self, parser):
        parser.add_argument("--name", required=True, help="Nombre del juego")

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
        name = options["name"]
        table = "games_game"
        idx_btree = "idx_game_name_btree"
        idx_hash = "idx_game_name_hash"

        report_dir = os.path.join(os.getcwd(), "reports")
        os.makedirs(report_dir, exist_ok=True)
        path = os.path.join(report_dir, f"report_name_{name}.md")
        lines = []

        explain_sql = f"EXPLAIN ANALYZE SELECT * FROM {table} WHERE name = %s;"

        with transaction.atomic():
            connection.cursor().execute(f"DROP INDEX IF EXISTS {idx_btree};")
        lines.append("## 1. Sin índice B-tree")
        lines.append("```")
        lines.extend(self.run_explain(explain_sql, [name]))
        lines.append("```")

        with transaction.atomic():
            connection.cursor().execute(
                f"CREATE INDEX IF NOT EXISTS {idx_btree} ON {table}(name);"
            )
        lines.append("## 2. Con índice B-tree")
        lines.append("```")
        lines.extend(self.run_explain(explain_sql, [name]))
        lines.append("```")

        lines.append("## 3. Tamaño índice B-tree")
        lines.append(f"- Tabla `{table}`: {self.get_size_pretty(table)}")
        lines.append(f"- Índice `{idx_btree}`: {self.get_size_pretty(idx_btree)}")

        with transaction.atomic():
            connection.cursor().execute(f"DROP INDEX IF EXISTS {idx_btree};")
        try:
            with transaction.atomic():
                connection.cursor().execute(
                    f"CREATE INDEX IF NOT EXISTS {idx_hash} ON {table} USING HASH (name);"
                )
            lines.append("## 4. Índice Hash")
            lines.append("```")
            lines.extend(self.run_explain(explain_sql, [name]))
            lines.append("```")
            lines.append(f"- Índice `{idx_hash}`: {self.get_size_pretty(idx_hash)}")
        except Exception as e:
            lines.append(f"_Hash no soportado: {e}_")

        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# Reporte búsqueda por name = '{name}'\n\n")
            f.write("\n".join(lines))

        self.stdout.write(f"Reporte guardado en {path}")
