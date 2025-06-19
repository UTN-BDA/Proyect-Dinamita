from django.core.management.base import BaseCommand
from games.models import Game
import csv
import os

class Command(BaseCommand):
    help = "Exporta la relación de cada juego con sus géneros a un CSV"

    def handle(self, *args, **kwargs):
        export_path = os.path.join(os.getcwd(), "game_genres.csv")
        with open(export_path, "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["app_id", "genre"])
            for game in Game.objects.exclude(genres__isnull=True).exclude(genres=""):
                genres = [g.strip() for g in game.genres.split(",") if g.strip()]
                for genre in genres:
                    writer.writerow([game.app_id, genre])
        self.stdout.write(self.style.SUCCESS(f"Relación juego-género exportada a {export_path}"))