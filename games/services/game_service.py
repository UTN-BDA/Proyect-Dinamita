
from django.db import transaction
from django.core.exceptions import ValidationError
from ..models import Games
from typing import Dict, List, Optional


class GameService:
    @staticmethod
    def create_game(game_data: Dict) -> Games:
        #Crea un nuevo juego con validaciones
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
        #Actualiza un juego existente
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
        #Obtiene un juego por su ID
        try:
            return Games.objects.get(app_id=app_id)
        except Games.DoesNotExist:
            return None

    @staticmethod
    def search_games(field: str, query: str) -> List[Games]:
        #Busca juegos por campo y término
        filter_kwargs = {f"{field}__icontains": query}
        return Games.objects.filter(**filter_kwargs)
