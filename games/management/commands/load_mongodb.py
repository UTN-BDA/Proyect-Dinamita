from django.core.management.base import BaseCommand
from games.mongodb_service import MongoDBService
import os


class Command(BaseCommand):
    help = "Cargar datos desde games_cleaned.json a MongoDB"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="dataset/games_cleaned.json",
            help="Ruta al archivo JSON (relativa al directorio del proyecto)",
        )

    def handle(self, *args, **options):
        file_path = options["file"]

        # Construir la ruta completa del archivo
        if not os.path.isabs(file_path):
            from django.conf import settings

            file_path = os.path.join(settings.BASE_DIR, file_path)

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"El archivo {file_path} no existe"))
            return

        self.stdout.write(f"Cargando datos desde {file_path}...")

        # Instanciar el servicio de MongoDB
        mongo_service = MongoDBService()

        # Cargar los datos
        success = mongo_service.load_games_from_json(file_path)

        if success:
            self.stdout.write(
                self.style.SUCCESS("Datos cargados exitosamente en MongoDB")
            )
        else:
            self.stdout.write(self.style.ERROR("Error al cargar los datos en MongoDB"))
