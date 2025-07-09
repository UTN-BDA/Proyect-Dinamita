from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Games, AboutGame, Genres
from typing import Dict, List, Optional


class GameService:
    @staticmethod
    def create_game(game_data: Dict) -> Games:
        """Crea un nuevo juego con validaciones"""
        with transaction.atomic():
            # Verificar si el juego ya existe
            if Games.objects.filter(app_id=game_data["app_id"]).exists():
                raise ValidationError(
                    f"El juego con ID {game_data['app_id']} ya existe"
                )

            game = Games.objects.create(**game_data)
            return game

    @staticmethod
    def update_game(app_id: str, game_data: Dict) -> Games:
        """Actualiza un juego existente"""
        with transaction.atomic():
            try:
                game = Games.objects.get(app_id=app_id)
                for field, value in game_data.items():
                    setattr(game, field, value)
                game.save()
                return game
            except Games.DoesNotExist:
                raise ValidationError(f"El juego con ID {app_id} no existe")

    @staticmethod
    def get_game(app_id: str) -> Optional[Games]:
        """Obtiene un juego por su ID"""
        try:
            return Games.objects.get(app_id=app_id)
        except Games.DoesNotExist:
            return None

    @staticmethod
    def search_games(field: str, query: str) -> List[Games]:
        """Busca juegos por campo y término"""
        filter_kwargs = {f"{field}__icontains": query}
        return Games.objects.filter(**filter_kwargs)


class AboutGameService:
    """Servicio para gestionar descripciones de juegos"""

    @staticmethod
    def update_or_create_description(app_id: str, description_data: Dict) -> AboutGame:
        """Crea o actualiza la descripción de un juego"""
        with transaction.atomic():
            game = GameService.get_game(app_id)
            if not game:
                raise ValidationError(f"El juego con ID {app_id} no existe")

            about_game, created = AboutGame.objects.update_or_create(
                app=game, defaults=description_data
            )
            return about_game

    @staticmethod
    def get_description(app_id: str) -> Optional[AboutGame]:
        """Obtiene la descripción de un juego"""
        try:
            game = Games.objects.get(app_id=app_id)
            return AboutGame.objects.get(app=game)
        except (Games.DoesNotExist, AboutGame.DoesNotExist):
            return None


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


class TransactionService:
    """Servicio principal para gestionar transacciones complejas (Facade Pattern)"""

    @staticmethod
    def create_complete_game(
        game_data: Dict, description_data: Dict = None, genres_list: List[str] = None
    ) -> Dict:
        """Crea un juego completo con descripción y géneros en una sola transacción"""
        with transaction.atomic():
            # Crear el juego base
            game = GameService.create_game(game_data)

            result = {"game": game}

            # Agregar descripción si se proporciona
            if description_data:
                description = AboutGameService.update_or_create_description(
                    game.app_id, description_data
                )
                result["description"] = description

            # Agregar géneros si se proporcionan
            if genres_list:
                genres = GenreService.update_game_genres(game.app_id, genres_list)
                result["genres"] = genres

            return result

    @staticmethod
    def update_complete_game(
        app_id: str,
        game_data: Dict = None,
        description_data: Dict = None,
        genres_list: List[str] = None,
    ) -> Dict:
        """Actualiza un juego completo en una sola transacción"""
        with transaction.atomic():
            result = {}

            # Actualizar datos básicos del juego
            if game_data:
                game = GameService.update_game(app_id, game_data)
                result["game"] = game

            # Actualizar descripción
            if description_data:
                description = AboutGameService.update_or_create_description(
                    app_id, description_data
                )
                result["description"] = description

            # Actualizar géneros
            if genres_list:
                genres = GenreService.update_game_genres(app_id, genres_list)
                result["genres"] = genres

            return result
