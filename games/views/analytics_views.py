"""
Vistas para análisis y gráficos
Aplicando principios SOLID - Interface Segregation
"""

from django.shortcuts import render, redirect
from django.db.models import Count
from django.db import connection, transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import time

from ..models import Genres


def graphs_by_gender(request):
    """Vista para gráficos por género - Refactorizada para ser más limpia"""

    # Manejar creación/eliminación de índice
    if request.method == "POST":
        action = request.POST.get("index_action")
        if action == "create":
            result = _manage_genre_index("create")
            if result and result["success"]:
                messages.success(
                    request, f"✅ Índice creado exitosamente. {result['message']}"
                )
            else:
                error_msg = result["message"] if result else "Error desconocido"
                messages.error(request, f"❌ Error al crear índice: {error_msg}")
        elif action == "drop":
            result = _manage_genre_index("drop")
            if result and result["success"]:
                messages.success(
                    request, f"✅ Índice eliminado exitosamente. {result['message']}"
                )
            else:
                error_msg = result["message"] if result else "Error desconocido"
                messages.error(request, f"❌ Error al eliminar índice: {error_msg}")

        return redirect("graphs_by_gender")

    # Verificar si existe índice y obtener datos
    index_exists = _check_genre_index_exists()
    start_time = time.time()

    if index_exists:
        # Usar consulta SQL optimizada con índice
        genre_data = _get_genre_statistics_optimized()
    else:
        # Usar consulta ORM normal
        genre_data = _get_genre_statistics()

    query_time = time.time() - start_time

    context = {
        "labels": genre_data["labels"],
        "data": genre_data["data"],
        "index_exists": index_exists,
        "query_time": round(query_time * 1000, 2),  # En milisegundos
        "total_genres": len(genre_data["labels"]),
        "total_games": sum(genre_data["data"]),
    }

    return render(request, "graphs_by_gender.html", context)


# Funciones auxiliares para análisis de datos (Single Responsibility)


def _get_genre_statistics():
    """Obtiene estadísticas de géneros de juegos usando ORM"""
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


def _get_genre_statistics_optimized():
    """Obtiene estadísticas de géneros usando SQL optimizado con índice"""
    with connection.cursor() as cursor:
        # SQL optimizado que aprovecha el índice en la columna genre
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


def _check_genre_index_exists():
    """Verifica si existe el índice para la columna genre"""
    with connection.cursor() as cursor:
        # Consulta para verificar si existe el índice idx_genres_genre_btree
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


def _manage_genre_index(action):
    """Gestiona la creación/eliminación del índice para géneros"""
    index_name = "idx_genres_genre_btree"

    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                if action == "create":
                    # Verificar si ya existe
                    if _check_genre_index_exists():
                        return {"success": False, "message": "El índice ya existe"}

                    # Crear índice B-tree en la columna genre
                    cursor.execute(
                        f'CREATE INDEX "{index_name}" ON "genres" USING BTREE ("genre");'
                    )

                    # Obtener información del índice creado
                    cursor.execute(
                        "SELECT pg_size_pretty(pg_relation_size(%s));", [index_name]
                    )
                    size_result = cursor.fetchone()
                    index_size = size_result[0] if size_result else "No disponible"

                    return {
                        "success": True,
                        "message": f"Índice creado. Tamaño: {index_size}",
                    }

                elif action == "drop":
                    # Verificar si existe antes de eliminar
                    if not _check_genre_index_exists():
                        return {"success": False, "message": "El índice no existe"}

                    # Eliminar índice
                    cursor.execute(f'DROP INDEX IF EXISTS "{index_name}";')
                    return {
                        "success": True,
                        "message": "Índice eliminado correctamente",
                    }

    except Exception as e:
        return {"success": False, "message": str(e)}


@login_required
def genre_performance_report(request):
    """Vista AJAX para generar reporte de rendimiento en tiempo real"""
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        return JsonResponse({"error": "Solo solicitudes AJAX permitidas"}, status=400)

    # Ejecutar consulta sin índice
    start_time = time.time()
    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute('DROP INDEX IF EXISTS "idx_genres_genre_btree";')

    no_index_time = time.time()
    genre_data_no_index = _get_genre_statistics()
    no_index_time = time.time() - no_index_time

    # Crear índice y ejecutar consulta con índice
    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(
                'CREATE INDEX IF NOT EXISTS "idx_genres_genre_btree" ON "genres" USING BTREE ("genre");'
            )

    with_index_time = time.time()
    genre_data_with_index = _get_genre_statistics_optimized()
    with_index_time = time.time() - with_index_time

    # Calcular mejora de rendimiento
    improvement = (
        ((no_index_time - with_index_time) / no_index_time) * 100
        if no_index_time > 0
        else 0
    )

    return JsonResponse(
        {
            "no_index_time": round(no_index_time * 1000, 2),
            "with_index_time": round(with_index_time * 1000, 2),
            "improvement_percentage": round(improvement, 2),
            "total_genres": len(genre_data_with_index["labels"]),
            "total_games": sum(genre_data_with_index["data"]),
        }
    )
