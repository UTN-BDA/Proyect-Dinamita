import pymongo
import json
import os
from django.conf import settings
from decimal import Decimal
from datetime import datetime


class MongoDBService:
    """Servicio para manejar operaciones con MongoDB"""

    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None

    def connect(self):
        """Conectar a MongoDB"""
        try:
            # Configuración de conexión a MongoDB
            mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
            self.client = pymongo.MongoClient(mongo_uri)
            self.db = self.client[os.getenv("MONGO_DB_NAME", "steam_games_db")]
            self.collection = self.db["games"]

            # Verificar conexión
            self.client.admin.command("ping")
            print("Conexión exitosa con MongoDB")
            return True
        except Exception as e:
            print(f"Error conectando con MongoDB: {e}")
            return False

    def disconnect(self):
        """Desconectar de MongoDB"""
        if self.client:
            self.client.close()

    def load_games_from_json(self, json_file_path):
        """Cargar juegos desde el archivo JSON a MongoDB"""
        try:
            if not self.connect():
                return False

            with open(json_file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Limpiar la colección existente
            self.collection.delete_many({})

            games_to_insert = []

            for app_id, game_data in data.items():
                # Preparar el documento del juego
                game_doc = {
                    "app_id": app_id,
                    "name": game_data.get("name", ""),
                    "release_date": game_data.get("release_date"),
                    "required_age": game_data.get("required_age"),
                    "price": (
                        float(game_data.get("price", 0))
                        if game_data.get("price")
                        else None
                    ),
                    "dlc_count": game_data.get("dlc_count"),
                    "detailed_description": game_data.get("detailed_description"),
                    "about_the_game": game_data.get("about_the_game"),
                    "short_description": game_data.get("short_description"),
                    "developers": game_data.get("developers", []),
                    "publishers": game_data.get("publishers", []),
                    "genres": game_data.get("genres", []),
                    "categories": game_data.get("categories", []),
                    "platforms": game_data.get("platforms", {}),
                    "user_score": game_data.get("user_score"),
                    "positive_reviews": game_data.get("positive"),
                    "negative_reviews": game_data.get("negative"),
                    "recommendations": game_data.get("recommendations"),
                    "achievements": game_data.get("achievements"),
                    "metacritic_score": game_data.get("metacritic_score"),
                    "metacritic_url": game_data.get("metacritic_url"),
                    "average_playtime_forever": game_data.get(
                        "average_playtime_forever"
                    ),
                    "average_playtime_2weeks": game_data.get("average_playtime_2weeks"),
                    "median_playtime_forever": game_data.get("median_playtime_forever"),
                    "median_playtime_2weeks": game_data.get("median_playtime_2weeks"),
                    "estimated_owners": game_data.get("estimated_owners"),
                    # Nuevos campos
                    "packages": game_data.get("packages", []),
                    "reviews": game_data.get("reviews"),
                    "urls": game_data.get("urls", {}),
                }

                games_to_insert.append(game_doc)

                # Insertar en lotes de 1000
                if len(games_to_insert) >= 1000:
                    self.collection.insert_many(games_to_insert)
                    print(f"Insertados {len(games_to_insert)} juegos...")
                    games_to_insert = []

            # Insertar los restantes
            if games_to_insert:
                self.collection.insert_many(games_to_insert)

            total_games = self.collection.count_documents({})
            print(f"Total de juegos cargados en MongoDB: {total_games}")

            # Crear índices para mejorar el rendimiento
            self.create_indexes()

            return True

        except Exception as e:
            print(f"Error cargando datos en MongoDB: {e}")
            return False
        finally:
            self.disconnect()

    def create_indexes(self):
        """Crear índices para mejorar el rendimiento"""
        try:
            self.collection.create_index("name")
            self.collection.create_index("price")
            self.collection.create_index("release_date")
            self.collection.create_index("genres")
            self.collection.create_index("developers")
            # Opcional: índices para nuevos campos si se busca por ellos
            # self.collection.create_index("reviews")
            # self.collection.create_index("urls.website")
            print("Índices creados exitosamente")
        except Exception as e:
            print(f"Error creando índices: {e}")

    def get_all_games(self, limit=None, skip=0):
        """Obtener todos los juegos"""
        try:
            if not self.connect():
                return []

            query = self.collection.find()
            if skip:
                query = query.skip(skip)
            if limit:
                query = query.limit(limit)

            return list(query)
        except Exception as e:
            print(f"Error obteniendo juegos: {e}")
            return []
        finally:
            self.disconnect()

    def search_games(self, search_term):
        """Buscar juegos por nombre"""
        try:
            if not self.connect():
                return []

            query = {"name": {"$regex": search_term, "$options": "i"}}

            return list(self.collection.find(query))
        except Exception as e:
            print(f"Error buscando juegos: {e}")
            return []
        finally:
            self.disconnect()

    def get_game_by_id(self, app_id):
        """Obtener un juego por su ID"""
        try:
            if not self.connect():
                return None

            return self.collection.find_one({"app_id": app_id})
        except Exception as e:
            print(f"Error obteniendo juego: {e}")
            return None
        finally:
            self.disconnect()

    def get_games_by_genre(self, genre):
        """Obtener juegos por género"""
        try:
            if not self.connect():
                return []

            query = {"genres": {"$in": [genre]}}

            return list(self.collection.find(query))
        except Exception as e:
            print(f"Error obteniendo juegos por género: {e}")
            return []
        finally:
            self.disconnect()

    def get_games_by_price_range(self, min_price, max_price):
        """Obtener juegos en un rango de precios"""
        try:
            if not self.connect():
                return []

            query = {"price": {"$gte": min_price, "$lte": max_price}}

            return list(self.collection.find(query))
        except Exception as e:
            print(f"Error obteniendo juegos por precio: {e}")
            return []
        finally:
            self.disconnect()
