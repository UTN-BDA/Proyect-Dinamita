from django.shortcuts import render, redirect
from .models import Game
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from collections import Counter


def registrar_usuario(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Inicia sesión automáticamente después del registro
            return redirect("game_search")  # Redirige al panel de control
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def game_search(request):
    fields = [
        ("app_id", "App ID"),
        ("name", "Nombre"),
        ("release_date", "Fecha de lanzamiento"),
        ("estimated_owners", "Dueños estimados"),
        ("peak_ccu", "Peak CCU"),
        ("required_age", "Edad requerida"),
        ("price", "Precio"),
    ]
    results = None
    selected_field = ""
    query = ""
    if request.GET.get("field") and request.GET.get("query"):
        selected_field = request.GET["field"]
        query = request.GET["query"]
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
    games = Game.objects.all()
    return render(request, "all.html", {"games": games})

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
