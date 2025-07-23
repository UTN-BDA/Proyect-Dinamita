"""
Servicio para gestión de géneros de juegos
Siguiendo principios SOLID - Single Responsibility
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from ..models import Games, Genres
from .game_service import GameService
from typing import List


class GenreService:
    """Servicio para gestionar géneros de juegos"""

    @staticmethod
    def update_game_genres(app_id: str, genres_list: List[str]) -> List[Genres]:
        """Actualiza los géneros de un juego"""
        with transaction.atomic():
            game = GameService.get_game(app_id)
            if not game:
                raise ValidationError(f"El juego con ID {app_id} no existe")

            # Eliminar géneros existentes
            Genres.objects.filter(app=game).delete()

            # Crear nuevos géneros
            new_genres = []
            for genre_name in genres_list:
                if genre_name.strip():  # Evitar géneros vacíos
                    genre = Genres.objects.create(app=game, genre=genre_name.strip())
                    new_genres.append(genre)

            return new_genres

    @staticmethod
    def get_game_genres(app_id: str) -> List[str]:
        """Obtiene los géneros de un juego"""
        try:
            game = Games.objects.get(app_id=app_id)
            return list(Genres.objects.filter(app=game).values_list("genre", flat=True))
        except Games.DoesNotExist:
            return []
