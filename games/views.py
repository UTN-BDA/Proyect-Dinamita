from django.shortcuts import render
from .models import Game, Genre
from collections import Counter
from django.core.paginator import Paginator


def game_search(request):
    fields = [
        ('app_id', 'App ID'),
        ('name', 'Nombre'),
        ('release_date', 'Fecha de lanzamiento'),
        ('estimated_owners', 'Dueños estimados'),
        ('peak_ccu', 'Peak CCU'),
        ('required_age', 'Edad requerida'),
        ('price', 'Precio'),
    ]
    results = None
    selected_field = ''
    query = ''
    if request.GET.get('field') and request.GET.get('query'):
        selected_field = request.GET['field']
        query = request.GET['query']
        filter_kwargs = {f"{selected_field}__icontains": query}
        results = Game.objects.filter(**filter_kwargs)
    return render(request, "query.html", {
        "fields": fields,
        "results": results,
        "selected_field": selected_field,
        "query": query,
    })

def home(request):
    return render(request, "home.html")

def all(request):
    # Obtener todos los generos del modelo Genre
    all_genres = Genre.objects.all()


    # Filtrar juegos por valor de genero
    genre_filter = request.GET.get('genre_filter', '')
    if genre_filter:
        games = Game.objects.filter(genres__icontains=genre_filter)
    else:
        games = Game.objects.all()

    # Filtrar juegos por letra inicial
    letter_filter = request.GET.get('letter_filter', '').upper()
    games = Game.objects.all()
    if letter_filter:
        games = games.filter(name__istartswith=letter_filter)
    else:
        letter_filter = 'A'  # Default to 'A' if no letter is selected
        games = games.filter(name__istartswith=letter_filter)
    games = games.order_by('name')  # Ordenar alfabéticamente por nombre
    paginator = Paginator(games, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "all.html", {
        "games": page_obj,
        "letter_filter": letter_filter,
        "all_genres": all_genres,
    })


def graphs_home(request):
    return render(request, "graphs_home.html")

def graphs_by_gender(request):
    # Obtener todos los géneros de los juegos
    all_genres = []
    for game in Game.objects.exclude(genres__isnull=True).exclude(genres=""):
        # Suponiendo que los géneros están separados por comas
        if game.genres is not None:
            all_genres.extend([g.strip() for g in game.genres.split(",") if g.strip()])
    genre_counts = Counter(all_genres)
    labels = list(genre_counts.keys())
    data = list(genre_counts.values())
    return render(request, "graphs_by_gender.html", {
        "labels": labels,
        "data": data,
    })