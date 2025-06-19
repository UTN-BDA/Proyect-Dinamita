from django.core.management.base import BaseCommand
from games.models import Game, Genre
import csv
import os

class Command(BaseCommand):
    help = "Importa la relación juego-género desde game_genres.csv al campo ManyToMany"

    def handle(self, *args, **kwargs):
        csv_path = os.path.join(os.getcwd(), "game_genres.csv")
        if not os.path.exists(csv_path):
            self.stderr.write(f"No se encontró el archivo {csv_path}")
            return

        with open(csv_path, newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for row in reader:
                app_id = row["app_id"]
                genre_name = row["genre"]
                try:
                    game = Game.objects.get(app_id=app_id)
                    genre, _ = Genre.objects.get_or_create(name=genre_name)
                    game.genres.add(genre)
                    count += 1
                except Game.DoesNotExist:
                    self.stderr.write(f"Juego con app_id {app_id} no encontrado.")
        self.stdout.write(self.style.SUCCESS(f"Relaciones importadas: {count}"))