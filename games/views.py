from django.shortcuts import render, redirect
from .models import Games, Genres
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
import subprocess
from django.conf import settings
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse
import os
from django.contrib import messages
from django.core.paginator import Paginator


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
        results = Games.objects.filter(**filter_kwargs)  # Fixed: use Game, not Games
    return render(
        request,
        "query.html",
        {
            "fields": fields,
            "results": results,
            "selected_field": selected_field,
            "query": query,
        },
    )


@login_required
def home(request):
    return render(request, "home.html")


def all(request):
    all_genres = Genres.objects.all()

    genre_filter = request.GET.get("genre_filter", "")
    letter_filter = request.GET.get("letter_filter", "").upper()

    games = Games.objects.all()

    if genre_filter:
        games = games.filter(genres__name=genre_filter)
    if letter_filter:
        games = games.filter(name__istartswith=letter_filter)
    # Elimina el else que fuerza la letra "A"

    games = games.order_by("name")
    paginator = Paginator(games, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "all.html",
        {
            "games": page_obj,
            "letter_filter": letter_filter,
            "all_genres": all_genres,
            "genre_filter": genre_filter,
        },
    )


@login_required
def graphs_home(request):
    return render(request, "graphs_home.html")


def graphs_by_gender(request):
    # Contar la cantidad de juegos por género usando el modelo actual
    from django.db.models import Count

    genre_counts = (
        Genres.objects.values("genre")
        .annotate(count=Count("app", distinct=True))
        .filter(genre__isnull=False)
        .order_by("-count")
    )
    labels = [g["genre"] for g in genre_counts]
    data = [g["count"] for g in genre_counts]
    return render(
        request,
        "graphs_by_gender.html",
        {
            "labels": labels,
            "data": data,
        },
    )


def backup_db(request):
    # 'request' is required by Django view signature even if not used
    backup_file = "steamdb_backup.sql"
    backup_path = os.path.join(settings.BASE_DIR, backup_file)
    db = settings.DATABASES["default"]
    cmd = [
        "pg_dump",
        "-h",
        db["HOST"],
        "-U",
        db["USER"],
        "-d",
        db["NAME"],
        "-f",
        backup_path,
    ]
    env = os.environ.copy()
    env["PGPASSWORD"] = db["PASSWORD"]
    try:
        subprocess.run(cmd, check=True, env=env)
        response = FileResponse(
            open(backup_path, "rb"), as_attachment=True, filename=backup_file
        )
        return response
    except Exception as e:
        return HttpResponse(f"Error al crear backup: {e}")


def restore_db(request):
    if request.method == "POST" and request.FILES.get("sql_file"):
        sql_file = request.FILES["sql_file"]
        db = settings.DATABASES["default"]
        restore_path = os.path.join(settings.BASE_DIR, "restore_temp.sql")
        with open(restore_path, "wb") as f:
            for chunk in sql_file.chunks():
                f.write(chunk)
        cmd = [
            "psql",
            "-h",
            db["HOST"],
            "-U",
            db["USER"],
            "-d",
            db["NAME"],
            "-f",
            restore_path,
        ]
        env = os.environ.copy()
        env["PGPASSWORD"] = db["PASSWORD"]
        try:
            subprocess.run(cmd, check=True, env=env)
            messages.success(request, "Restauración completada correctamente.")
        except Exception as e:
            messages.error(request, f"Error al restaurar: {e}")
        return HttpResponseRedirect(reverse("home"))
    return render(request, "restore.html")


def view_db_schema(request):
    from django.apps import apps
    from django.db import models

    models_info = []
    for model in apps.get_models():
        model_name = model.__name__
        fields = []
        fks = []
        m2ms = []
        for field in model._meta.get_fields():
            if isinstance(field, models.ForeignKey):
                fks.append(f"{field.name} → {field.related_model.__name__}")
            elif isinstance(field, models.ManyToManyField):
                m2ms.append(f"{field.name} ↔ {field.related_model.__name__}")
            elif hasattr(field, "attname"):
                fields.append(field.attname)
        models_info.append(
            {
                "model": model_name,
                "fields": fields,
                "foreign_keys": fks,
                "many_to_many": m2ms,
            }
        )
    svg_height = (len(models_info) + 1) * 120
    return render(
        request,
        "db_schema.html",
        {"models_info": models_info, "svg_height": svg_height},
    )
