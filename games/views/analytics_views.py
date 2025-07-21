"""
Vistas para análisis y gráficos
Aplicando principios SOLID - Interface Segregation
"""

from django.shortcuts import render
from django.db.models import Count

from ..models import Genres


def graphs_by_gender(request):
    """Vista para gráficos por género - Refactorizada para ser más limpia"""

    # Obtener datos de géneros
    genre_data = _get_genre_statistics()

    context = {
        "labels": genre_data["labels"],
        "data": genre_data["data"],
    }

    return render(request, "graphs_by_gender.html", context)


# Funciones auxiliares para análisis de datos (Single Responsibility)


def _get_genre_statistics():
    """Obtiene estadísticas de géneros de juegos"""
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
