#!/usr/bin/env python
"""
Script de prueba manual para verificar las funcionalidades de la base de datos
"""
import os
import django
import sys

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "steam_db.settings")
django.setup()

from games.mongodb_service import MongoDBService
from games.database_service import DatabaseService
from games.models import Games, Genres


def test_mongodb_connection():
    """Test básico de conexión a MongoDB"""
    print("🔍 Probando conexión a MongoDB...")
    try:
        mongo_service = MongoDBService()
        connected = mongo_service.connect()
        if connected:
            print("✅ Conexión a MongoDB exitosa")

            # Verificar si hay datos
            if mongo_service.collection:
                count = mongo_service.collection.count_documents({})
                print(f"📊 Documentos en MongoDB: {count}")

            mongo_service.disconnect()
            return True
        else:
            print("❌ No se pudo conectar a MongoDB")
            return False
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        return False


def test_database_service():
    """Test del servicio unificado de base de datos"""
    print("\n🔍 Probando DatabaseService...")

    # Test con base relacional
    try:
        relational_service = DatabaseService("relational")
        print("✅ DatabaseService relacional inicializado")

        # Contar juegos en BD relacional
        games_count = Games.objects.count()
        print(f"📊 Juegos en PostgreSQL: {games_count}")

    except Exception as e:
        print(f"❌ Error con DatabaseService relacional: {e}")

    # Test con MongoDB
    try:
        mongodb_service = DatabaseService("mongodb")
        print("✅ DatabaseService MongoDB inicializado")

        # Test de búsqueda (simulado)
        # results = mongodb_service.search_games("name", "test")
        # print(f"🔍 Resultados de búsqueda simulada: {len(results)}")

    except Exception as e:
        print(f"❌ Error con DatabaseService MongoDB: {e}")


def test_basic_models():
    """Test básico de modelos Django"""
    print("\n🔍 Probando modelos Django...")

    try:
        # Verificar estructura de tablas
        games_count = Games.objects.count()
        genres_count = Genres.objects.count()

        print(f"📊 Total de juegos: {games_count}")
        print(f"📊 Total de géneros: {genres_count}")

        if games_count > 0:
            sample_game = Games.objects.first()
            print(f"🎮 Juego de ejemplo: {sample_game.name} (ID: {sample_game.app_id})")

        if genres_count > 0:
            sample_genre = Genres.objects.first()
            print(f"🏷️ Género de ejemplo: {sample_genre.genre}")

        print("✅ Modelos Django funcionando correctamente")

    except Exception as e:
        print(f"❌ Error con modelos Django: {e}")


def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas del sistema de bases de datos")
    print("=" * 50)

    # Test 1: Modelos básicos
    test_basic_models()

    # Test 2: Conexión MongoDB
    mongodb_ok = test_mongodb_connection()

    # Test 3: Servicio unificado
    test_database_service()

    print("\n" + "=" * 50)
    print("✅ Pruebas completadas")

    if mongodb_ok:
        print("\n📝 Nota: MongoDB está funcionando correctamente.")
        print("   Puedes usar la aplicación para cambiar entre bases de datos.")
    else:
        print("\n⚠️  Nota: MongoDB no está disponible.")
        print("   La aplicación funcionará solo con PostgreSQL.")

    print("\n🌐 Para probar la interfaz web, ejecuta:")
    print("   python manage.py runserver")


if __name__ == "__main__":
    main()
