from django.conf import settings
from .models import Games, Genres
from .mongodb_service import MongoDBService
from django.core.paginator import Paginator
import time
from datetime import datetime


class DatabaseService:
    """Servicio para manejar operaciones con diferentes tipos de bases de datos"""

    def __init__(self, db_type="relational"):
        """
        Inicializar el servicio con el tipo de base de datos
        db_type: 'relational' o 'mongodb'
        """
        self.db_type = db_type
        self.last_query_time = None
        if db_type == "mongodb":
            self.mongo_service = MongoDBService()

    def get_last_query_time(self):
        """Obtener el tiempo de la última consulta en milisegundos"""
        return self.last_query_time

    def _measure_time(self, func, *args, **kwargs):
        """Medir el tiempo de ejecución de una función"""
        start_time = time.perf_counter()  # Más preciso que time.time()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        self.last_query_time = round(
            (end_time - start_time) * 1000, 3
        )  # 3 decimales para más precisión
        return result

    def get_all_games(self, page=1, per_page=10, genre_filter=None, letter_filter=None):
        """Obtener todos los juegos con paginación y filtros"""
        if self.db_type == "mongodb":
            return self._measure_time(
                self._get_mongo_games, page, per_page, genre_filter, letter_filter
            )
        else:
            return self._measure_time(
                self._get_relational_games, page, per_page, genre_filter, letter_filter
            )

    def search_games(self, field, query):
        """Buscar juegos por campo y término de búsqueda"""
        if self.db_type == "mongodb":
            return self._measure_time(self._search_mongo_games, field, query)
        else:
            return self._measure_time(self._search_relational_games, field, query)

    def get_game_by_id(self, app_id):
        """Obtener un juego por su ID"""
        if self.db_type == "mongodb":
            return self._measure_time(self.mongo_service.get_game_by_id, app_id)
        else:

            def _get_relational_game_by_id(app_id):
                try:
                    return Games.objects.get(app_id=app_id)
                except Games.DoesNotExist:
                    return None

            return self._measure_time(_get_relational_game_by_id, app_id)

    def get_genre_statistics(self):
        """Obtener estadísticas por género"""
        if self.db_type == "mongodb":
            return self._measure_time(self._get_mongo_genre_stats)
        else:
            return self._measure_time(self._get_relational_genre_stats)

    def get_all_genres(self):
        """Obtener todos los géneros disponibles"""
        if self.db_type == "mongodb":
            return self._measure_time(self._get_mongo_genres)
        else:

            def _get_relational_genres():
                return Genres.objects.all()

            return self._measure_time(_get_relational_genres)

    def _get_relational_games(self, page, per_page, genre_filter, letter_filter):
        """Obtener juegos de la base de datos relacional"""
        games = Games.objects.all()

        if genre_filter:
            games = games.filter(genres__name=genre_filter)
        if letter_filter:
            games = games.filter(name__istartswith=letter_filter)

        games = games.order_by("name")
        paginator = Paginator(games, per_page)
        page_obj = paginator.get_page(page)

        return {
            "games": page_obj,
            "has_previous": page_obj.has_previous(),
            "has_next": page_obj.has_next(),
            "previous_page_number": (
                page_obj.previous_page_number() if page_obj.has_previous() else None
            ),
            "next_page_number": (
                page_obj.next_page_number() if page_obj.has_next() else None
            ),
            "page_number": page_obj.number,
            "num_pages": paginator.num_pages,
        }

    def _get_mongo_games(self, page, per_page, genre_filter, letter_filter):
        """Obtener juegos de MongoDB"""
        skip = (page - 1) * per_page

        # Construir filtro para MongoDB
        query = {}
        if genre_filter:
            query["genres"] = {"$in": [genre_filter]}
        if letter_filter:
            query["name"] = {"$regex": f"^{letter_filter}", "$options": "i"}

        # Conectar primero (tiempo de conexión no cuenta)
        if not self.mongo_service.connect() or self.mongo_service.collection is None:
            return self._empty_page_result()

        try:
            # SOLO medir el tiempo de las operaciones de base de datos
            start_time = time.perf_counter()

            # Contar total de documentos
            total_count = self.mongo_service.collection.count_documents(query)

            # Obtener documentos con paginación
            games_cursor = (
                self.mongo_service.collection.find(query)
                .sort("name", 1)
                .skip(skip)
                .limit(per_page)
            )
            games = list(games_cursor)

            end_time = time.perf_counter()
            self.last_query_time = round((end_time - start_time) * 1000, 3)

            # Calcular información de paginación
            total_pages = (total_count + per_page - 1) // per_page
            has_previous = page > 1
            has_next = page < total_pages

            return {
                "games": games,
                "has_previous": has_previous,
                "has_next": has_next,
                "previous_page_number": page - 1 if has_previous else None,
                "next_page_number": page + 1 if has_next else None,
                "page_number": page,
                "num_pages": total_pages,
            }
        finally:
            self.mongo_service.disconnect()

    def _search_relational_games(self, field, query):
        """Buscar en la base de datos relacional"""
        filter_kwargs = {f"{field}__icontains": query}
        return Games.objects.filter(**filter_kwargs)

    def _search_mongo_games(self, field, query):
        """Buscar en MongoDB"""
        if field == "name":
            # Conectar primero
            if (
                not self.mongo_service.connect()
                or self.mongo_service.collection is None
            ):
                return []

            try:
                # Medir solo la consulta
                start_time = time.perf_counter()
                mongo_query = {"name": {"$regex": query, "$options": "i"}}
                results = list(self.mongo_service.collection.find(mongo_query))
                end_time = time.perf_counter()
                self.last_query_time = round((end_time - start_time) * 1000, 3)
                return results
            finally:
                self.mongo_service.disconnect()
        else:
            # Para otros campos, crear una búsqueda más genérica
            if (
                not self.mongo_service.connect()
                or self.mongo_service.collection is None
            ):
                return []

            try:
                start_time = time.perf_counter()
                mongo_query = {field: {"$regex": query, "$options": "i"}}
                results = list(self.mongo_service.collection.find(mongo_query))
                end_time = time.perf_counter()
                self.last_query_time = round((end_time - start_time) * 1000, 3)
                return results
            finally:
                self.mongo_service.disconnect()

    def _get_relational_genre_stats(self):
        """Obtener estadísticas de géneros de la BD relacional"""
        from django.db.models import Count

        genre_counts = (
            Genres.objects.values("genre")
            .annotate(count=Count("app", distinct=True))
            .filter(genre__isnull=False)
            .order_by("-count")
        )

        labels = [g["genre"] for g in genre_counts]
        data = [g["count"] for g in genre_counts]

        return {"labels": labels, "data": data}

    def _get_mongo_genre_stats(self):
        """Obtener estadísticas de géneros de MongoDB"""
        if not self.mongo_service.connect() or self.mongo_service.collection is None:
            return {"labels": [], "data": []}

        try:
            # Medir solo la agregación
            start_time = time.perf_counter()

            # Agregación para contar juegos por género
            pipeline = [
                {"$unwind": "$genres"},
                {"$group": {"_id": "$genres", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
            ]

            results = list(self.mongo_service.collection.aggregate(pipeline))

            end_time = time.perf_counter()
            self.last_query_time = round((end_time - start_time) * 1000, 3)

            labels = [result["_id"] for result in results if result["_id"]]
            data = [result["count"] for result in results if result["_id"]]

            return {"labels": labels, "data": data}
        finally:
            self.mongo_service.disconnect()

    def _get_mongo_genres(self):
        """Obtener todos los géneros únicos de MongoDB"""
        if not self.mongo_service.connect() or self.mongo_service.collection is None:
            return []

        try:
            # Medir solo la consulta distinct
            start_time = time.perf_counter()
            genres = self.mongo_service.collection.distinct("genres")
            end_time = time.perf_counter()
            self.last_query_time = round((end_time - start_time) * 1000, 3)

            # Convertir a formato similar al modelo Django
            return [{"genre": genre} for genre in genres if genre]
        finally:
            self.mongo_service.disconnect()

    def _empty_page_result(self):
        """Retornar resultado vacío para paginación"""
        return {
            "games": [],
            "has_previous": False,
            "has_next": False,
            "previous_page_number": None,
            "next_page_number": None,
            "page_number": 1,
            "num_pages": 1,
        }
