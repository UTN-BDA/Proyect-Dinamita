"""
Script único para importar datos de JSON a MongoDB
Lee el archivo games_export.json y lo carga en MongoDB
"""

import os
import django
import json
import sys
import pymongo
from decimal import Decimal
from datetime import datetime

print("Configurando Django...")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "steam_db.settings")
django.setup()


class MongoDBImporter:
    """Importador de datos a MongoDB"""

    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None

    def connect(self):
        """Conectar a MongoDB"""
        try:
            # Configuración de MongoDB
            mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
            db_name = os.getenv("MONGO_DB_NAME", "steam_games_db")

            print(f"Conectando a MongoDB: {mongo_uri}")
            self.client = pymongo.MongoClient(mongo_uri)
            self.db = self.client[db_name]
            self.collection = self.db["games"]

            # Verificar conexión
            self.client.admin.command("ping")
            print("✓ Conexión a MongoDB exitosa")
            return True

        except Exception as e:
            print(f"✗ Error conectando a MongoDB: {e}")
            return False

    def disconnect(self):
        """Desconectar de MongoDB"""
        if self.client:
            self.client.close()

    def load_json_to_mongo(self, json_file_path):
        """Cargar datos del JSON a MongoDB"""
        try:
            # Verificar que el archivo existe
            if not os.path.exists(json_file_path):
                print(f"ERROR: No se encontró el archivo {json_file_path}")
                return False

            # Leer archivo JSON
            print(f"Leyendo archivo: {json_file_path}")
            with open(json_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not data:
                print("ERROR: El archivo JSON está vacío")
                return False

            print(f"Datos cargados: {len(data)} juegos")

            # Conectar a MongoDB
            if not self.connect():
                return False

            # Verificar que la colección existe
            if self.collection is None:
                print("ERROR: No se pudo conectar a la colección")
                return False

            # Limpiar colección existente
            print("Limpiando colección existente...")
            self.collection.delete_many({})

            # Preparar documentos para inserción
            games_to_insert = []

            for app_id, game_data in data.items():
                # Crear documento para MongoDB
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
                    "achievements": game_data.get("achievements"),
                    "estimated_owners": game_data.get("estimated_owners"),
                    # Descripciones
                    "detailed_description": game_data.get("detailed_description"),
                    "about_the_game": game_data.get("about_the_game"),
                    "short_description": game_data.get("short_description"),
                    # Listas
                    "audio_languages": game_data.get("audio_languages", []),
                    "categories": game_data.get("categories", []),
                    "developers": game_data.get("developers", []),
                    "genres": game_data.get("genres", []),
                    "languages": game_data.get("languages", []),
                    "publishers": game_data.get("publishers", []),
                    # Metacritic
                    "metacritic_score": game_data.get("metacritic_score"),
                    "metacritic_url": game_data.get("metacritic_url"),
                    # Packages
                    "packages": game_data.get("packages", []),
                    # Platforms
                    "platforms": game_data.get("platforms", {}),
                    # Playtime
                    "average_playtime_forever": game_data.get(
                        "average_playtime_forever"
                    ),
                    "average_playtime_2weeks": game_data.get("average_playtime_2weeks"),
                    "median_playtime_forever": game_data.get("median_playtime_forever"),
                    "median_playtime_2weeks": game_data.get("median_playtime_2weeks"),
                    # Reviews y scores
                    "reviews": game_data.get("reviews"),
                    "user_score": game_data.get("user_score"),
                    "score_rank": game_data.get("score_rank"),
                    "positive": game_data.get("positive"),
                    "negative": game_data.get("negative"),
                    "recommendations": game_data.get("recommendations"),
                    # URLs
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
                print(f"Insertados {len(games_to_insert)} juegos finales...")

            # Verificar inserción
            total_inserted = self.collection.count_documents({})
            print(f"✓ Total de juegos insertados en MongoDB: {total_inserted}")

            # Crear índices básicos
            self.create_indexes()

            return True

        except json.JSONDecodeError as e:
            print(f"ERROR: El archivo JSON está malformado: {e}")
            return False
        except Exception as e:
            print(f"ERROR: {e}")
            return False
        finally:
            self.disconnect()

    def create_indexes(self):
        """Crear índices para mejorar el rendimiento"""
        try:
            if self.collection is None:
                print(
                    "Advertencia: No se pudo acceder a la colección para crear índices"
                )
                return

            print("Creando índices...")
            self.collection.create_index("app_id")
            self.collection.create_index("name")
            self.collection.create_index("price")
            self.collection.create_index("genres")
            self.collection.create_index("developers")
            print("✓ Índices creados exitosamente")
        except Exception as e:
            print(f"Advertencia: Error creando índices: {e}")


def main():
    """Función principal"""
    json_file = "games_export.json"

    print("=" * 50)
    print("IMPORTANDO DATOS DE JSON A MONGODB")
    print("=" * 50)

    try:
        importer = MongoDBImporter()
        success = importer.load_json_to_mongo(json_file)

        if success:
            print("\n" + "=" * 50)
            print("✓ IMPORTACIÓN COMPLETADA EXITOSAMENTE")
            print("Los datos han sido cargados en MongoDB")
            print("=" * 50)
            return True
        else:
            print("\n" + "=" * 50)
            print("✗ ERROR EN LA IMPORTACIÓN")
            print("=" * 50)
            return False

    except Exception as e:
        print(f"ERROR CRÍTICO: {e}")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nProceso interrumpido por el usuario.")
        sys.exit(1)
