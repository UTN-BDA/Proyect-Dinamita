"""
Servicio de transacciones complejas (Facade Pattern)
Coordina múltiples servicios en transacciones atómicas
"""

from django.db import transaction
from .game_service import GameService
from .about_game_service import AboutGameService
from .genre_service import GenreService
from typing import Dict, List


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
