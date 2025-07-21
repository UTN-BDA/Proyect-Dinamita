"""
Vistas para búsquedas y listados de juegos
Aplicando principios DRY y Single Responsibility
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from ..models import Games, Genres
from ..config import SEARCH_FIELDS, PAGINATION_SIZE


@login_required
def game_search(request):
    """Vista de búsqueda de juegos - Refactorizada para ser más limpia"""

    context = {
        "fields": SEARCH_FIELDS,
        "results": None,
        "selected_field": "",
        "query": "",
    }

    # Procesar búsqueda si hay parámetros
    if request.GET.get("field") and request.GET.get("query"):
        selected_field = request.GET["field"]
        query = request.GET["query"]

        # Actualizar contexto con datos de búsqueda
        context.update(
            {
                "selected_field": selected_field,
                "query": query,
                "results": _perform_game_search(selected_field, query),
            }
        )

    return render(request, "query.html", context)


def all_games(request):
    """Vista para mostrar todos los juegos con filtros - Refactorizada"""

    # Obtener todos los géneros para el filtro
    all_genres = Genres.objects.all()

    # Obtener filtros de la URL
    filters = _extract_filters(request)

    # Aplicar filtros y obtener juegos
    games = _apply_filters_to_games(filters)

    # Paginación
    page_obj = _paginate_games(games, request.GET.get("page"))

    context = {
        "games": page_obj,
        "all_genres": all_genres,
        **filters,  # Spread de filtros para el template
    }

    return render(request, "all.html", context)


# Funciones auxiliares para mantener las vistas limpias (Single Responsibility)


def _perform_game_search(field: str, query: str):
    """Realiza búsqueda de juegos por campo específico"""
    filter_kwargs = {f"{field}__icontains": query}
    return Games.objects.filter(**filter_kwargs)


def _extract_filters(request):
    """Extrae y normaliza filtros de la request"""
    return {
        "genre_filter": request.GET.get("genre_filter", ""),
        "letter_filter": request.GET.get("letter_filter", "").upper(),
    }


def _apply_filters_to_games(filters):
    """Aplica filtros a la consulta de juegos"""
    games = Games.objects.all()

    if filters["genre_filter"]:
        games = games.filter(genres__genre=filters["genre_filter"])

    if filters["letter_filter"]:
        games = games.filter(name__istartswith=filters["letter_filter"])

    return games.order_by("name")


def _paginate_games(games, page_number):
    """Aplica paginación a los juegos"""
    paginator = Paginator(games, PAGINATION_SIZE)
    return paginator.get_page(page_number)
