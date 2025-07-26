
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse

from ..models import Games, Genres
from ..config import SEARCH_FIELDS, PAGINATION_SIZE


@login_required
def game_search(request):
    """Vista de búsqueda de juegos - Refactorizada"""

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
    """Vista optimizada para mostrar solo ID y nombre de juegos"""

    # Obtener filtros de la URL
    filters = _extract_filters(request)

    # Aplicar filtros pero solo cargar ID y nombre 
    games = _apply_filters_to_games_optimized(filters)

    # Paginación con más elementos por página para listas simples
    page_obj = _paginate_games(games, request.GET.get("page"), page_size=50)

    # Solo obtener géneros únicos si se necesita filtrar
    all_genres = (
        Genres.objects.values("genre").distinct() if not filters["genre_filter"] else []
    )

    context = {
        "games": page_obj,
        "all_genres": all_genres,
        **filters,  
    }

    return render(request, "all.html", context)


def game_details_ajax(request, app_id):
    """Vista AJAX para obtener detalles de un juego específico"""
    try:
        game = Games.objects.get(app_id=app_id)
        data = {
            "success": True,
            "game": {
                "app_id": game.app_id,
                "name": game.name,
                "rel_date": (
                    game.rel_date.strftime("%d/%m/%Y") if game.rel_date else "N/A"
                ),
                "price": f"${game.price}" if game.price else "Gratis",
                "req_age": game.req_age or "N/A",
                "estimated_owners": game.estimated_owners or "N/A",
                "achievements": game.achievements or 0,
                "dlc_count": game.dlc_count or 0,
            },
        }
    except Games.DoesNotExist:
        data = {"success": False, "error": "Juego no encontrado"}

    return JsonResponse(data)




def _perform_game_search(field: str, query: str):
    #Realiza búsqueda de juegos por campo específico
    filter_kwargs = {f"{field}__icontains": query}
    return Games.objects.filter(**filter_kwargs)


def _extract_filters(request):
    #Extrae y normaliza filtros de la request
    return {
        "genre_filter": request.GET.get("genre_filter", ""),
        "letter_filter": request.GET.get("letter_filter", "").upper(),
    }


def _apply_filters_to_games(filters):
    #Aplica filtros a la consulta de juegos
    games = Games.objects.all()

    if filters["genre_filter"]:
        games = games.filter(genres__genre=filters["genre_filter"])

    if filters["letter_filter"]:
        games = games.filter(name__istartswith=filters["letter_filter"])

    return games.order_by("name")


def _apply_filters_to_games_optimized(filters):
    games = Games.objects.only("app_id", "name")

    if filters["genre_filter"]:
        games = games.filter(genres__genre=filters["genre_filter"])

    if filters["letter_filter"]:
        games = games.filter(name__istartswith=filters["letter_filter"])

    return games.order_by("name")


def _paginate_games(games, page_number, page_size=None):
    #Aplica paginación a los juegos
    if page_size is None:
        page_size = PAGINATION_SIZE

    paginator = Paginator(games, page_size)
    return paginator.get_page(page_number)
