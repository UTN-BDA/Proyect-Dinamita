"""
Vistas para análisis de géneros de juegos
Principio: Single Responsibility - Solo maneja análisis de géneros
"""

import time
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

# Importación relativa para evitar problemas de módulos
from ...services.analytics import GenreAnalyticsService, PerformanceService


@login_required
def graphs_by_gender(request):
    """Vista principal para gráficos por género"""

    # Manejar acciones de índice
    if request.method == "POST":
        action = request.POST.get("index_action")
        result = _handle_index_action(action)

        if result:
            if result["success"]:
                messages.success(request, f"✅ {result['message']}")
            else:
                messages.error(request, f"❌ {result['message']}")

        return redirect("graphs_by_gender")

    # Obtener datos y métricas
    context = _get_genre_analysis_context()
    return render(request, "graphs_by_gender.html", context)


@login_required
def genre_performance_report(request):
    """Vista AJAX para reporte de rendimiento en tiempo real"""
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        return JsonResponse({"error": "Solo solicitudes AJAX permitidas"}, status=400)

    try:
        # Medir rendimiento
        performance_data = PerformanceService.measure_query_performance()

        # Obtener datos adicionales
        genre_data = GenreAnalyticsService.get_genre_statistics_optimized()
        genre_summary = GenreAnalyticsService.get_genre_summary(genre_data)

        # Combinar resultados
        response_data = {**performance_data, **genre_summary}

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse(
            {"error": f"Error al generar reporte: {str(e)}"}, status=500
        )


# Funciones auxiliares - Keep It Simple Principle
def _handle_index_action(action: str) -> dict:
    """Maneja acciones sobre índices de género"""
    if action == "create":
        return PerformanceService.create_genre_index()
    elif action == "drop":
        return PerformanceService.drop_genre_index()
    else:
        return {"success": False, "message": "Acción no válida"}


def _get_genre_analysis_context() -> dict:
    """Prepara contexto para análisis de géneros"""
    # Verificar índice
    index_exists = GenreAnalyticsService.check_genre_index_exists()

    # Medir tiempo de consulta
    start_time = time.time()

    if index_exists:
        genre_data = GenreAnalyticsService.get_genre_statistics_optimized()
    else:
        genre_data = GenreAnalyticsService.get_genre_statistics()

    query_time = time.time() - start_time
    genre_summary = GenreAnalyticsService.get_genre_summary(genre_data)

    return {
        "labels": genre_data["labels"],
        "data": genre_data["data"],
        "index_exists": index_exists,
        "query_time": round(query_time * 1000, 2),  # En milisegundos
        **genre_summary,
    }
