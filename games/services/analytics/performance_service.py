
import time
from django.db import connection, transaction
from typing import Dict

from .genre_service import GenreAnalyticsService


class PerformanceService:
    #Maneja análisis de rendimiento y gestión de índices

    INDEX_NAME = "idx_genres_genre_btree"

    @staticmethod
    def create_genre_index() -> Dict[str, any]:
        #Crea índice para géneros
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    # Verificar si ya existe
                    if GenreAnalyticsService.check_genre_index_exists():
                        return {"success": False, "message": "El índice ya existe"}

                    # Crear índice
                    cursor.execute(
                        f'CREATE INDEX "{PerformanceService.INDEX_NAME}" ON "genres" USING BTREE ("genre");'
                    )

                    # Obtener tamaño
                    cursor.execute(
                        "SELECT pg_size_pretty(pg_relation_size(%s));",
                        [PerformanceService.INDEX_NAME],
                    )
                    size_result = cursor.fetchone()
                    index_size = size_result[0] if size_result else "No disponible"

                    return {
                        "success": True,
                        "message": f"Índice creado. Tamaño: {index_size}",
                    }

        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def drop_genre_index() -> Dict[str, any]:
        #Elimina índice de géneros
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    # Verificar si existe
                    if not GenreAnalyticsService.check_genre_index_exists():
                        return {"success": False, "message": "El índice no existe"}

                    # Eliminar índice
                    cursor.execute(
                        f'DROP INDEX IF EXISTS "{PerformanceService.INDEX_NAME}";'
                    )

                    return {
                        "success": True,
                        "message": "Índice eliminado correctamente",
                    }

        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def measure_query_performance() -> Dict[str, float]:
        #Mide rendimiento de consultas con y sin índice

        # Consulta sin índice
        PerformanceService.drop_genre_index()

        start_time = time.time()
        GenreAnalyticsService.get_genre_statistics()
        no_index_time = time.time() - start_time

        # Crear índice y consultar
        PerformanceService.create_genre_index()

        start_time = time.time()
        GenreAnalyticsService.get_genre_statistics_optimized()
        with_index_time = time.time() - start_time

        # Calcular mejora
        improvement = (
            ((no_index_time - with_index_time) / no_index_time) * 100
            if no_index_time > 0
            else 0
        )

        return {
            "no_index_time": round(no_index_time * 1000, 2),
            "with_index_time": round(with_index_time * 1000, 2),
            "improvement_percentage": round(improvement, 2),
        }
