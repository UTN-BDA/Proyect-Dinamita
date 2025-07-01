from django.core.management.base import BaseCommand
from games.mongodb_service import MongoDBService
import os


class Command(BaseCommand):
    help = "Cargar datos de games_cleaned.json en MongoDB"

    def add_arguments(self, parser):
        parser.add_argument(
            "--json-file",
            type=str,
            default="dataset/games_cleaned.json",
            help="Ruta al archivo JSON (relativa al directorio del proyecto)",
        )

    def handle(self, *args, **options):
        json_file = options["json_file"]

        # Construir la ruta completa
        if not os.path.isabs(json_file):
            from django.conf import settings

            json_file = os.path.join(settings.BASE_DIR, json_file)

        if not os.path.exists(json_file):
            self.stdout.write(self.style.ERROR(f"El archivo {json_file} no existe"))
            return

        self.stdout.write(f"Cargando datos desde: {json_file}")
        self.stdout.write("Esto puede tomar varios minutos...")

        mongo_service = MongoDBService()
        success = mongo_service.load_games_from_json(json_file)

        if success:
            self.stdout.write(
                self.style.SUCCESS("Datos cargados exitosamente en MongoDB")
            )
        else:
            self.stdout.write(self.style.ERROR("Error cargando datos en MongoDB"))
