import json
from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError
from django.db.utils import DataError
from games.models import Game


class Command(BaseCommand):
    help = "Importa los juegos desde un JSON a la base de datos"

    def handle(self, *args, **kwargs):
        json_path = r"C:\Users\Francisco\Downloads\archive\games.json"

        def safe_truncate(val, max_len):
            if val is None:
                return None
            s = str(val)
            return s if len(s) <= max_len else s[:max_len]

        imported = 0
        errors = 0

        # Cargar JSON
        try:
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self.stderr.write(f"Error al leer JSON: {e}")
            return

        # Iterar claves (app_id) y valores
        for app_id, info in data.items():
            try:
                # Preparar lista de tags
                raw_tags = info.get("tags", {})
                if isinstance(raw_tags, list):
                    tags_list = raw_tags
                elif isinstance(raw_tags, dict):
                    tags_list = list(raw_tags.keys())
                else:
                    tags_list = []

                with transaction.atomic():
                    game, created = Game.objects.get_or_create(
                        app_id=safe_truncate(app_id, 20),
                        defaults={
                            "name": safe_truncate(info.get("name"), 255),
                            "release_date": safe_truncate(info.get("release_date"), 50),
                            "estimated_owners": safe_truncate(
                                info.get("estimated_owners"), 50
                            ),
                            "peak_ccu": info.get("peak_ccu") or 0,
                            "required_age": info.get("required_age") or 0,
                            "price": info.get("price") or 0,
                            "about_game": safe_truncate(
                                info.get("about_the_game")
                                or info.get("detailed_description"),
                                10000,
                            ),
                            "developers": safe_truncate(
                                ",".join(info.get("developers", [])), 1000
                            ),
                            "publishers": safe_truncate(
                                ",".join(info.get("publishers", [])), 1000
                            ),
                            "categories": safe_truncate(
                                ",".join(info.get("categories", [])), 1000
                            ),
                            "genres": safe_truncate(
                                ",".join(info.get("genres", [])), 1000
                            ),
                            "tags": safe_truncate(",".join(tags_list), 2000),
                            "screenshots": safe_truncate(
                                ",".join(info.get("screenshots", [])), 200
                            ),
                            "movies": safe_truncate(
                                ",".join(info.get("movies", [])), 200
                            ),
                        },
                    )
                    if created:
                        imported += 1
            except (IntegrityError, ValueError, DataError) as exc:
                self.stderr.write(f"Error importando AppID {app_id}: {exc}")
                errors += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Importación completada: {imported} juegos importados, {errors} errores."
            )
        )
