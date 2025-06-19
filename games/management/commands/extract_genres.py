from django.core.management.base import BaseCommand
from games.models import Game

class Command(BaseCommand):
    help = "Extrae todos los géneros únicos de la tabla Game"

    def handle(self, *args, **kwargs):
        unique_genres = set()
        for game in Game.objects.exclude(genres__isnull=True).exclude(genres=""):
            if game.genres is not None:
                genres = [g.strip() for g in game.genres.split(",") if g.strip()]
                unique_genres.update(genres)
        self.stdout.write("Géneros únicos encontrados:")
        for genre in sorted(unique_genres):
            self.stdout.write(f"- {genre}")