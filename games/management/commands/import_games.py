import csv
import sys
from datetime import datetime
from django.core.management.base import BaseCommand
from games.models import Game

# Aumenta el límite de tamaño de campo para CSV con campos muy largos
csv.field_size_limit(sys.maxsize)


def parse_bool(val):
    """
    Convierte cadenas como 'True', 'true', '1', 'yes' en True;
    todo lo demás (incluyendo '', None) -> False.
    """
    if val is None:
        return False
    v = str(val).strip().lower()
    return v in ("true", "1", "yes")


def parse_int(val):
    """Convierte a int; si falla o está vacío, devuelve None."""
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def parse_float(val):
    """Convierte a float; si falla o está vacío, devuelve None."""
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def parse_range(val):
    """
    Si llega 'min - max', devuelve el promedio como int.
    Si es un solo número, lo devuelve como int.
    Si no se puede parsear, devuelve None.
    """
    if not val:
        return None
    parts = [p.strip() for p in str(val).split("-")]
    try:
        nums = list(map(int, parts))
    except ValueError:
        return None
    return sum(nums) // len(nums)


class Command(BaseCommand):
    help = "Importa datos desde un CSV al modelo Game"

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            type=str,
            default=r"F:\OneDrive - frsr.utn.edu.ar\4TO ING EN SISTEMAS\BASE DE DATOS AVANZADA\steam_dataset\games.csv",
            help="Ruta al archivo CSV a importar",
        )

    def handle(self, *args, **options):
        path = options["path"]
        total, created = 0, 0

        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                total += 1

                # Parseo de fecha, intenta YYYY-MM-DD, si falla deja None
                rd = None
                try:
                    rd = datetime.strptime(
                        row.get("Release date", ""), "%Y-%m-%d"
                    ).date()
                except Exception:
                    pass

                obj, was_created = Game.objects.update_or_create(
                    appid=row.get("AppID"),
                    defaults={
                        "name": row.get("Name"),
                        "release_date": rd,
                        "estimated_owners": parse_range(row.get("Estimated owners")),
                        "peak_ccu": parse_int(row.get("Peak CCU")),
                        "required_age": parse_int(row.get("Required age")),
                        "price": parse_float(row.get("Price")),
                        "discount_dlc_count": parse_int(row.get("DiscountDLC count")),
                        "about_the_game": row.get("About the game"),
                        "supported_languages": row.get("Supported languages"),
                        "full_audio_languages": row.get("Full audio languages"),
                        "reviews": row.get("Reviews"),
                        "header_image": row.get("Header image"),
                        "website": row.get("Website"),
                        "support_url": row.get("Support url"),
                        "support_email": row.get("Support email"),
                        "windows": parse_bool(row.get("Windows")),
                        "mac": parse_bool(row.get("Mac")),
                        "linux": parse_bool(row.get("Linux")),
                        "metacritic_score": parse_int(row.get("Metacritic score")),
                        "metacritic_url": row.get("Metacritic url"),
                        "user_score": parse_float(row.get("User score")),
                        "positive": parse_int(row.get("Positive")),
                        "negative": parse_int(row.get("Negative")),
                        "score_rank": parse_int(row.get("Score rank")),
                        "achievements": parse_int(row.get("Achievements")),
                        "recommendations": parse_int(row.get("Recommendations")),
                        "notes": row.get("Notes"),
                        "average_playtime_forever": parse_int(
                            row.get("Average playtime forever")
                        ),
                        "average_playtime_two_weeks": parse_int(
                            row.get("Average playtime two weeks")
                        ),
                        "median_playtime_forever": parse_int(
                            row.get("Median playtime forever")
                        ),
                        "median_playtime_two_weeks": parse_int(
                            row.get("Median playtime two weeks")
                        ),
                        "developers": row.get("Developers"),
                        "publishers": row.get("Publishers"),
                        "categories": row.get("Categories"),
                        "genres": row.get("Genres"),
                        "tags": row.get("Tags"),
                        "screenshots": row.get("Screenshots"),
                        "movies": row.get("Movies"),
                    },
                )

                if was_created:
                    created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Importación completada: {total} filas procesadas, {created} registros nuevos."
            )
        )
