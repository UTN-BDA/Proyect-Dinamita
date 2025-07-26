from django.apps import apps
from django.db import models
from typing import List, Dict
from .security_service import SecurityService


class SchemaService:
    """Maneja análisis del schema de la base de datos"""

    @staticmethod
    def get_models_info() -> List[Dict]:
        """Obtiene información de modelos permitidos"""
        models_info = []

        try:
            games_app = apps.get_app_config("games")
            for model in games_app.get_models():
                table_name = model._meta.db_table

                # Solo incluir tablas permitidas por seguridad
                if SecurityService.validate_table_name(table_name):
                    model_data = SchemaService._analyze_model(model)
                    models_info.append(model_data)

        except LookupError:
            # Fallback con lista blanca estricta
            for model in apps.get_models():
                if (
                    model._meta.app_label == "games"
                    and SecurityService.validate_table_name(model._meta.db_table)
                ):
                    model_data = SchemaService._analyze_model(model)
                    models_info.append(model_data)

        return models_info

    @staticmethod
    def get_available_tables() -> List[Dict]:
        """Obtiene tablas disponibles para operaciones administrativas"""
        tables = []

        try:
            games_app = apps.get_app_config("games")
            for model in games_app.get_models():
                table_name = model._meta.db_table

                # Solo incluir tablas permitidas por seguridad
                if SecurityService.validate_table_name(table_name):
                    tables.append(
                        {
                            "model_name": model.__name__,
                            "db_table": table_name,
                        }
                    )

        except LookupError:
            # Fallback con lista blanca estricta
            for model in apps.get_models():
                if (
                    model._meta.app_label == "games"
                    and SecurityService.validate_table_name(model._meta.db_table)
                ):
                    tables.append(
                        {
                            "model_name": model.__name__,
                            "db_table": model._meta.db_table,
                        }
                    )

        return tables

    @staticmethod
    def get_table_translations() -> Dict[str, str]:
        """Obtiene traducciones de nombres de tablas"""
        return {
            "about_game": "Acerca del Juego",
            "audio_languages": "Idiomas de Audio",
            "developers": "Desarrolladores",
            "games": "Juegos",
            "genres": "Géneros",
            "languages": "Idiomas",
            "packages": "Paquetes",
            "platforms": "Plataformas",
            "publishers": "Distribuidores",
            "categories": "Categorías",
            "reviews": "Reseñas",
            "playtime": "Tiempo de Juego",
            "urls": "URLs",
            "metacritic": "Metacritic",
            "scores_and_ranks": "Puntuaciones y Rankings",
        }

    @staticmethod
    def _analyze_model(model) -> Dict:
        """Analiza un modelo específico"""
        model_name = model.__name__
        fields = []
        foreign_keys = []
        many_to_many = []

        for field in model._meta.get_fields():
            if isinstance(field, models.ForeignKey):
                foreign_keys.append(f"{field.name} → {field.related_model.__name__}")
            elif isinstance(field, models.ManyToManyField):
                many_to_many.append(f"{field.name} ↔ {field.related_model.__name__}")
            elif hasattr(field, "attname"):
                fields.append(field.attname)

        return {
            "model": model_name,
            "fields": fields,
            "foreign_keys": foreign_keys,
            "many_to_many": many_to_many,
        }
