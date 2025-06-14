from django.shortcuts import render
from .models import Game
from collections import Counter
import subprocess
from django.conf import settings
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse
import os
from django.contrib import messages


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
    return render(
        request,
        "graphs_by_gender.html",
        {
            "labels": labels,
            "data": data,
        },
    )


def backup_db(request):

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
