import os  # manejar rutas y sistema de ficheros
from django.core.management.base import BaseCommand
from django.db import connection, transaction


class Command(BaseCommand):
    """
    Comando que automatiza:
      - Eliminación de índices si existen
      - Creación de índice B-tree y Hash sobre `required_age` y `price`
      - Ejecución de EXPLAIN ANALYZE para consultas filtrando por rangos de edad y precio
      - Medición de tamaño de tabla e índices
      - Generación de informe Markdown
    """

    help = (
        "Automatiza pruebas de índices (B-tree y Hash) sobre `required_age` y `price` en `games_game`, "
        "incluyendo EXPLAIN ANALYZE y tamaño de índice."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--age-min",
            dest="age_min",
            required=True,
            help="Edad mínima para el rango de required_age (ej. 18)",
        )
        parser.add_argument(
            "--age-max",
            dest="age_max",
            required=True,
            help="Edad máxima para el rango de required_age (ej. 30)",
        )
        parser.add_argument(
            "--price-min",
            dest="price_min",
            required=True,
            help="Precio mínimo para el rango de price (ej. 10)",
        )
        parser.add_argument(
            "--price-max",
            dest="price_max",
            required=True,
            help="Precio máximo para el rango de price (ej. 300)",
        )

    def run_explain(self, sql, params=None):
        with connection.cursor() as cursor:
            cursor.execute(sql, params or [])
            return [row[0] for row in cursor.fetchall()]

    def get_size_pretty(self, relation):
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_size_pretty(pg_relation_size(%s));", [relation])
            return cursor.fetchone()[0]

    def handle(self, *args, **options):
        age_min = options["age_min"]
        age_max = options["age_max"]
        price_min = options["price_min"]
        price_max = options["price_max"]

        table = "games_game"
        idx_btree = "idx_games_game_age_price"
        idx_hash = "idx_games_game_age_price_hs"

        report_dir = os.path.join(os.getcwd(), "reports")
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(
            report_dir,
            f"report_age_{age_min}_{age_max}_price_{price_min}_{price_max}.md",
        )

        explain_sql = (
            f"EXPLAIN ANALYZE SELECT * FROM {table} "
            f"WHERE required_age BETWEEN %s AND %s AND price BETWEEN %s AND %s;"
        )

        lines = []

        # --- Sin índice ---
        with transaction.atomic():
            connection.cursor().execute(f"DROP INDEX IF EXISTS {idx_btree};")
            connection.cursor().execute(f"DROP INDEX IF EXISTS {idx_hash};")

        lines.append(
            f"# Informe de índices: required_age BETWEEN {age_min} y {age_max}, price BETWEEN {price_min} y {price_max}\n"
        )
        size_table = self.get_size_pretty(table)
        lines.append(f"- Tamaño tabla `{table}`: {size_table}\n")

        lines.append("## 1. Sin índice")
        plan = self.run_explain(explain_sql, [age_min, age_max, price_min, price_max])
        lines.append("```sql")
        lines.extend(plan)
        lines.append("```")

        # --- Crear índice B-tree ---
        lines.append("## 2. Índice B-tree (required_age, price)")
        lines.append("```sql")
        lines.append(f"CREATE INDEX {idx_btree} ON {table}(required_age, price);")
        lines.append("```")
        with transaction.atomic():
            connection.cursor().execute(
                f"CREATE INDEX {idx_btree} ON {table}(required_age, price);"
            )
        lines.append("### Consulta con índice B-tree")
        plan = self.run_explain(explain_sql, [age_min, age_max, price_min, price_max])
        lines.append("```sql")
        lines.extend(plan)
        lines.append("```")
        size_btree = self.get_size_pretty(idx_btree)
        lines.append(f"- Tamaño índice B-tree: {size_btree}\n")

        # --- Crear índice HASH ---
        with transaction.atomic():
            connection.cursor().execute(f"DROP INDEX IF EXISTS {idx_btree};")

        lines.append("## 3. Índice Hash (required_age, price)")
        lines.append("```sql")
        lines.append(
            f"CREATE INDEX {idx_hash} ON {table} USING HASH (required_age, price);"
        )
        lines.append("```")
        try:
            with transaction.atomic():
                connection.cursor().execute(
                    f"CREATE INDEX {idx_hash} ON {table} USING HASH (required_age, price);"
                )
            lines.append("### Consulta con índice Hash")
            plan = self.run_explain(
                explain_sql, [age_min, age_max, price_min, price_max]
            )
            lines.append("```sql")
            lines.extend(plan)
            lines.append("```")
            size_hash = self.get_size_pretty(idx_hash)
            lines.append(f"- Tamaño índice Hash: {size_hash}\n")
        except Exception as e:
            lines.append(f"_Índice Hash no soportado o falló: {e}_\n")

        # Escribir informe
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        self.stdout.write(f"Reporte guardado en {report_path}")
