from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch, MagicMock
import json
import os
from .mongodb_service import MongoDBService
from .database_service import DatabaseService
from .models import Games, Genres


class MongoDBServiceTest(TestCase):
    """Tests para el servicio de MongoDB"""

    def setUp(self):
        self.mongo_service = MongoDBService()
        self.test_data = {
            "12345": {
                "name": "Test Game",
                "release_date": "2023-01-01",
                "required_age": 18,
                "price": 29.99,
                "dlc_count": 2,
                "detailed_description": "A test game description",
                "about_the_game": "About this test game",
                "short_description": "Short description",
                "developers": ["Test Developer"],
                "publishers": ["Test Publisher"],
                "genres": ["Action", "Adventure"],
                "categories": ["Single-player"],
                "platforms": {"windows": True, "mac": False},
                "user_score": 85,
                "positive": 1000,
                "negative": 100,
                "recommendations": 900,
                "achievements": 50,
                "metacritic_score": 82,
                "metacritic_url": "http://test.com",
                "average_playtime_forever": 120,
                "average_playtime_2weeks": 30,
                "median_playtime_forever": 100,
                "median_playtime_2weeks": 25,
                "estimated_owners": "1,000,000 - 2,000,000",
            }
        }

    @patch("pymongo.MongoClient")
    def test_connect_success(self, mock_client):
        """Test conexión exitosa a MongoDB"""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.admin.command.return_value = True

        result = self.mongo_service.connect()

        self.assertTrue(result)
        mock_client.assert_called_once()
        mock_client_instance.admin.command.assert_called_once_with("ping")

    @patch("pymongo.MongoClient")
    def test_connect_failure(self, mock_client):
        """Test fallo en la conexión a MongoDB"""
        mock_client.side_effect = Exception("Connection failed")

        result = self.mongo_service.connect()

        self.assertFalse(result)

    @patch.object(MongoDBService, "connect")
    @patch.object(MongoDBService, "disconnect")
    def test_search_games(self, mock_disconnect, mock_connect):
        """Test búsqueda de juegos por nombre"""
        mock_connect.return_value = True
        mock_collection = MagicMock()
        self.mongo_service.collection = mock_collection

        expected_results = [{"name": "Test Game", "app_id": "12345"}]
        mock_collection.find.return_value = expected_results

        results = self.mongo_service.search_games("Test")

        self.assertEqual(results, expected_results)
        mock_collection.find.assert_called_once_with(
            {"name": {"$regex": "Test", "$options": "i"}}
        )

    @patch.object(MongoDBService, "connect")
    @patch.object(MongoDBService, "disconnect")
    def test_get_game_by_id(self, mock_disconnect, mock_connect):
        """Test obtener juego por ID"""
        mock_connect.return_value = True
        mock_collection = MagicMock()
        self.mongo_service.collection = mock_collection

        expected_game = {"name": "Test Game", "app_id": "12345"}
        mock_collection.find_one.return_value = expected_game

        result = self.mongo_service.get_game_by_id("12345")

        self.assertEqual(result, expected_game)
        mock_collection.find_one.assert_called_once_with({"app_id": "12345"})

    @patch.object(MongoDBService, "connect")
    @patch.object(MongoDBService, "disconnect")
    def test_get_games_by_genre(self, mock_disconnect, mock_connect):
        """Test obtener juegos por género"""
        mock_connect.return_value = True
        mock_collection = MagicMock()
        self.mongo_service.collection = mock_collection

        expected_results = [{"name": "Action Game", "genres": ["Action"]}]
        mock_collection.find.return_value = expected_results

        results = self.mongo_service.get_games_by_genre("Action")

        self.assertEqual(results, expected_results)
        mock_collection.find.assert_called_once_with({"genres": {"$in": ["Action"]}})


class DatabaseServiceTest(TestCase):
    """Tests para el servicio unificado de base de datos"""

    def setUp(self):
        self.relational_service = DatabaseService("relational")
        self.mongodb_service = DatabaseService("mongodb")

        # Crear datos de prueba para BD relacional
        self.test_game = Games.objects.create(
            app_id="12345",
            name="Test Game",
            rel_date="2023-01-01",
            req_age=18,
            price=29.99,
            estimated_owners="1,000,000",
        )
        self.test_genre = Genres.objects.create(app=self.test_game, genre="Action")

    def test_init_relational(self):
        """Test inicialización con base de datos relacional"""
        service = DatabaseService("relational")
        self.assertEqual(service.db_type, "relational")
        self.assertFalse(hasattr(service, "mongo_service"))

    def test_init_mongodb(self):
        """Test inicialización con MongoDB"""
        service = DatabaseService("mongodb")
        self.assertEqual(service.db_type, "mongodb")
        self.assertTrue(hasattr(service, "mongo_service"))
        self.assertIsInstance(service.mongo_service, MongoDBService)

    def test_get_game_by_id_relational(self):
        """Test obtener juego por ID en base relacional"""
        result = self.relational_service.get_game_by_id("12345")

        self.assertIsNotNone(result)
        self.assertEqual(result.app_id, "12345")
        self.assertEqual(result.name, "Test Game")

    def test_get_game_by_id_not_found(self):
        """Test obtener juego inexistente"""
        result = self.relational_service.get_game_by_id("99999")
        self.assertIsNone(result)

    @patch.object(MongoDBService, "get_game_by_id")
    def test_get_game_by_id_mongodb(self, mock_get_game):
        """Test obtener juego por ID en MongoDB"""
        expected_game = {"app_id": "12345", "name": "Test Game"}
        mock_get_game.return_value = expected_game

        result = self.mongodb_service.get_game_by_id("12345")

        self.assertEqual(result, expected_game)
        mock_get_game.assert_called_once_with("12345")

    def test_search_games_relational(self):
        """Test búsqueda en base relacional"""
        results = self.relational_service.search_games("name", "Test")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Test Game")

    @patch.object(MongoDBService, "search_games")
    def test_search_games_mongodb_by_name(self, mock_search):
        """Test búsqueda por nombre en MongoDB"""
        expected_results = [{"name": "Test Game", "app_id": "12345"}]
        mock_search.return_value = expected_results

        results = self.mongodb_service.search_games("name", "Test")

        self.assertEqual(results, expected_results)
        mock_search.assert_called_once_with("Test")

    def test_get_all_genres_relational(self):
        """Test obtener géneros en base relacional"""
        genres = self.relational_service.get_all_genres()

        # genres es un QuerySet de Django
        self.assertEqual(len(list(genres)), 1)
        first_genre = genres.first()
        self.assertEqual(first_genre.genre, "Action")

    @patch.object(MongoDBService, "connect")
    @patch.object(MongoDBService, "disconnect")
    def test_get_all_genres_mongodb(self, mock_disconnect, mock_connect):
        """Test obtener géneros en MongoDB"""
        mock_connect.return_value = True
        mock_collection = MagicMock()
        self.mongodb_service.mongo_service.collection = mock_collection

        mock_collection.distinct.return_value = ["Action", "Adventure"]

        genres = self.mongodb_service.get_all_genres()

        expected_genres = [{"genre": "Action"}, {"genre": "Adventure"}]
        self.assertEqual(genres, expected_genres)

    def test_get_relational_games_pagination(self):
        """Test paginación en base relacional"""
        # Crear más juegos para probar paginación
        for i in range(15):
            Games.objects.create(app_id=f"game_{i}", name=f"Game {i}", price=10.99)

        result = self.relational_service.get_all_games(page=1, per_page=10)

        self.assertEqual(len(result["games"]), 10)
        self.assertTrue(result["has_next"])
        self.assertFalse(result["has_previous"])
        self.assertEqual(result["page_number"], 1)

    @patch.object(MongoDBService, "connect")
    @patch.object(MongoDBService, "disconnect")
    def test_get_mongo_games_pagination(self, mock_disconnect, mock_connect):
        """Test paginación en MongoDB"""
        mock_connect.return_value = True
        mock_collection = MagicMock()
        self.mongodb_service.mongo_service.collection = mock_collection

        # Simular 25 documentos totales
        mock_collection.count_documents.return_value = 25
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_collection.find.return_value = mock_cursor

        # Simular 10 juegos en la página 1
        mock_games = [{"name": f"Game {i}", "app_id": f"{i}"} for i in range(10)]
        mock_cursor.__iter__.return_value = iter(mock_games)
        list(mock_cursor)  # Esto activa __iter__

        result = self.mongodb_service.get_all_games(page=1, per_page=10)

        self.assertTrue(result["has_next"])
        self.assertFalse(result["has_previous"])
        self.assertEqual(result["page_number"], 1)
        self.assertEqual(result["num_pages"], 3)  # 25 / 10 = 3 páginas

    def test_query_time_measurement(self):
        """Test que el tiempo de consulta se mide correctamente"""
        service = DatabaseService("relational")

        # Ejecutar una consulta
        result = service.get_all_games(page=1, per_page=5)

        # Verificar que el tiempo se midió
        query_time = service.get_last_query_time()
        self.assertIsNotNone(query_time)
        if query_time is not None:
            self.assertGreater(query_time, 0)
            self.assertIsInstance(query_time, (int, float))

    def test_query_time_in_context(self):
        """Test que el tiempo de consulta se incluye en el contexto de las vistas"""
        self.client.login(username="testuser", password="testpass123")

        response = self.client.get(reverse("all_games"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("query_time", response.context)

        query_time = response.context["query_time"]
        if query_time is not None:
            self.assertGreater(query_time, 0)

    def test_query_time_search(self):
        """Test medición de tiempo en búsquedas"""
        self.client.login(username="testuser", password="testpass123")

        response = self.client.get(
            reverse("game_search"), {"field": "name", "query": "Test"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("query_time", response.context)

    @patch.object(MongoDBService, "connect")
    @patch.object(MongoDBService, "disconnect")
    def test_mongodb_query_time_measurement(self, mock_disconnect, mock_connect):
        """Test medición de tiempo con MongoDB"""
        mock_connect.return_value = True

        service = DatabaseService("mongodb")
        mock_collection = MagicMock()
        service.mongo_service.collection = mock_collection

        # Simular respuesta
        mock_collection.count_documents.return_value = 0
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_collection.find.return_value = mock_cursor
        list(mock_cursor)  # Simular iteración

        # Ejecutar consulta
        result = service.get_all_games()

        # Verificar que se midió el tiempo
        query_time = service.get_last_query_time()
        self.assertIsNotNone(query_time)
        if query_time is not None:
            self.assertGreaterEqual(query_time, 0)


class ViewsTest(TestCase):
    """Tests para las vistas de la aplicación"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

        # Crear datos de prueba
        self.test_game = Games.objects.create(
            app_id="12345",
            name="Test Game",
            rel_date="2023-01-01",
            req_age=18,
            price=29.99,
        )
        self.test_genre = Genres.objects.create(app=self.test_game, genre="Action")

    def test_home_view_requires_login(self):
        """Test que la vista home requiere autenticación"""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_home_view_authenticated(self):
        """Test vista home con usuario autenticado"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "relational")  # Default db_type

    def test_switch_database_to_mongodb(self):
        """Test cambio a MongoDB"""
        self.client.login(username="testuser", password="testpass123")

        response = self.client.post(reverse("switch_database"), {"db_type": "mongodb"})

        self.assertEqual(response.status_code, 302)  # Redirect

        # Verificar que la sesión se actualizó
        session = self.client.session
        self.assertEqual(session.get("db_type"), "mongodb")

    def test_switch_database_invalid_type(self):
        """Test cambio con tipo de BD inválido"""
        self.client.login(username="testuser", password="testpass123")

        response = self.client.post(
            reverse("switch_database"), {"db_type": "invalid_db"}
        )

        self.assertEqual(response.status_code, 302)

        # La sesión no debe cambiar
        session = self.client.session
        self.assertNotEqual(session.get("db_type"), "invalid_db")

    def test_database_status_view(self):
        """Test vista de estado de bases de datos"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("database_status"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PostgreSQL")
        self.assertContains(response, "MongoDB")

    def test_game_search_view_get(self):
        """Test vista de búsqueda sin parámetros"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("game_search"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Búsqueda de Juegos")

    def test_game_search_view_with_query(self):
        """Test vista de búsqueda con parámetros"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(
            reverse("game_search"), {"field": "name", "query": "Test"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Game")

    def test_all_games_view(self):
        """Test vista de todos los juegos"""
        response = self.client.get(reverse("all_games"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Game")

    def test_all_games_view_with_filters(self):
        """Test vista de juegos con filtros"""
        response = self.client.get(
            reverse("all_games"), {"genre_filter": "Action", "letter_filter": "T"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Game")

    @patch.object(MongoDBService, "connect")
    def test_graphs_by_gender_mongodb(self, mock_connect):
        """Test gráficos con MongoDB"""
        self.client.login(username="testuser", password="testpass123")

        # Configurar sesión para usar MongoDB
        session = self.client.session
        session["db_type"] = "mongodb"
        session.save()

        mock_connect.return_value = False  # Simular conexión fallida

        response = self.client.get(reverse("graphs_by_gender"))

        self.assertEqual(response.status_code, 200)


class IntegrationTest(TestCase):
    """Tests de integración completos"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="integrationuser", password="testpass123"
        )

    def test_complete_workflow_relational(self):
        """Test flujo completo con base de datos relacional"""
        # Login
        self.client.login(username="integrationuser", password="testpass123")

        # Verificar que estamos usando BD relacional por defecto
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

        # Ir a estado de bases de datos
        response = self.client.get(reverse("database_status"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PostgreSQL")

        # Verificar que podemos ver todos los juegos
        response = self.client.get(reverse("all_games"))
        self.assertEqual(response.status_code, 200)

    def test_complete_workflow_mongodb(self):
        """Test flujo completo con MongoDB"""
        self.client.login(username="integrationuser", password="testpass123")

        # Cambiar a MongoDB
        response = self.client.post(reverse("switch_database"), {"db_type": "mongodb"})
        self.assertEqual(response.status_code, 302)

        # Verificar cambio
        session = self.client.session
        self.assertEqual(session.get("db_type"), "mongodb")

        # Verificar que la vista home muestra MongoDB
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_session_persistence(self):
        """Test que la sesión persiste el tipo de BD"""
        self.client.login(username="integrationuser", password="testpass123")

        # Cambiar a MongoDB
        self.client.post(reverse("switch_database"), {"db_type": "mongodb"})

        # Navegar a diferentes páginas y verificar que se mantiene
        pages = ["home", "game_search", "all_games", "database_status"]

        for page in pages:
            response = self.client.get(reverse(page))
            self.assertEqual(response.status_code, 200)

            # Verificar que la sesión sigue teniendo mongodb
            session = self.client.session
            self.assertEqual(session.get("db_type"), "mongodb")
