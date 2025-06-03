from django.shortcuts import render
from .models import Game

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
    games = Game.objects.all()
    return render(request, "all.html", {"games": games})