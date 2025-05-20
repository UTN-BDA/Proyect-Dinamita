import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError
from django.db.utils import DataError
from games.models import Game


class Command(BaseCommand):
    help = "Importa los juegos desde el archivo CSV a la base de datos"

    def handle(self, *args, **kwargs):
        csv_path = r"C:\Users\Francisco\Documents\GitHub\Proyect-Dinamita\games.csv"

        # Función para truncar cadenas a un máximo de longitud
        def safe_truncate(val, max_len):
            if pd.isna(val):
                return None
            s = str(val)
            return s if len(s) <= max_len else s[:max_len]

        imported = 0
        errors = 0

        # Leer CSV con pandas
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            self.stderr.write(f"Error al leer CSV con pandas: {e}")
            return

        # Iterar filas e importar
        for _, row in df.iterrows():
            try:
                with transaction.atomic():
                    game, created = Game.objects.get_or_create(
                        app_id=safe_truncate(row["AppID"], 20),
                        defaults={
                            "name": safe_truncate(row["Name"], 255),
                            "release_date": safe_truncate(row["Release date"], 50),
                            "estimated_owners": safe_truncate(
                                row["Estimated owners"], 50
                            ),
                            "peak_ccu": (
                                int(row["Peak CCU"])
                                if not pd.isna(row["Peak CCU"])
                                else 0
                            ),
                            "required_age": (
                                float(row["Required age"])
                                if not pd.isna(row["Required age"])
                                else 0
                            ),
                            "price": (
                                float(row["Price"]) if not pd.isna(row["Price"]) else 0
                            ),
                            "about_game": safe_truncate(row["About the game"], 10000),
                            "developers": safe_truncate(row["Developers"], 1000),
                            "publishers": safe_truncate(row["Publishers"], 1000),
                            "categories": safe_truncate(row["Categories"], 1000),
                            "genres": safe_truncate(row["Genres"], 1000),
                            "tags": safe_truncate(row["Tags"], 2000),
                            "screenshots": safe_truncate(row["Screenshots"], 200),
                            "movies": safe_truncate(row["Movies"], 200),
                        },
                    )
                    if created:
                        imported += 1
            except (IntegrityError, ValueError, DataError) as exc:
                self.stderr.write(f"Error importando AppID {row.get('AppID')}: {exc}")
                errors += 1

        # Resultado final
        self.stdout.write(
            self.style.SUCCESS(
                f"Importación completada: {imported} juegos importados, {errors} errores."
            )
        )
