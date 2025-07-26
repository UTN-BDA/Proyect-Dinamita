from django.db import transaction
from django.core.exceptions import ValidationError
from ..models import Games, AboutGame
from .game_service import GameService
from typing import Dict, Optional


class AboutGameService:

    @staticmethod
    def update_or_create_description(app_id: str, description_data: Dict) -> AboutGame:
        #Crea o actualiza la descripción de un juego
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
        #Obtiene la descripción de un juego
        try:
            game = Games.objects.get(app_id=app_id)
            return AboutGame.objects.get(app=game)
        except (Games.DoesNotExist, AboutGame.DoesNotExist):
            return None
