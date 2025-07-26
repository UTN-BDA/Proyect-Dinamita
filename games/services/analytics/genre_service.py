from django.db.models import Count
from django.db import connection
from typing import Dict, List

from games.models import Genres


class GenreAnalyticsService:
    """Maneja análisis y estadísticas de géneros de juegos"""

    @staticmethod
    def get_genre_statistics() -> Dict[str, List]:
        #Obtiene estadísticas de géneros usando ORM
        genre_counts = (
            Genres.objects.values("genre")
            .annotate(count=Count("app", distinct=True))
            .filter(genre__isnull=False)
            .order_by("-count")
        )

        return {
            "labels": [g["genre"] for g in genre_counts],
            "data": [g["count"] for g in genre_counts],
        }

    @staticmethod
    def get_genre_statistics_optimized() -> Dict[str, List]:
        #Obtiene estadísticas optimizadas usando SQL directo
        with connection.cursor() as cursor:
            sql = """
            SELECT g.genre, COUNT(DISTINCT g.app_id) as count
            FROM genres g
            WHERE g.genre IS NOT NULL
            GROUP BY g.genre
            ORDER BY count DESC
            """
            cursor.execute(sql)
            results = cursor.fetchall()

        return {
            "labels": [row[0] for row in results],
            "data": [row[1] for row in results],
        }

    @staticmethod
    def get_genre_summary(genre_data: Dict[str, List]) -> Dict[str, int]:
        #Obtiene resumen de estadísticas de géneros
        return {
            "total_genres": len(genre_data["labels"]),
            "total_games": sum(genre_data["data"]),
            "top_genre": genre_data["labels"][0] if genre_data["labels"] else "N/A",
            "top_genre_count": genre_data["data"][0] if genre_data["data"] else 0,
        }

    @staticmethod
    def check_genre_index_exists() -> bool:
        #Verifica si existe el índice para géneros
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1 FROM pg_indexes 
                    WHERE tablename = 'genres' 
                    AND indexname = 'idx_genres_genre_btree'
                )
                """
            )
            result = cursor.fetchone()
            return result[0] if result else False
