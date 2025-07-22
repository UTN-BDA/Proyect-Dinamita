from django.shortcuts import render, redirect
from .models import Games, Genres
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
import subprocess
import time
from django.conf import settings
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse
import os
from django.contrib import messages
from django.core.paginator import Paginator
from .database_service import DatabaseService


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
def home(request):
    # Obtener el tipo de base de datos seleccionado desde la sesión
    db_type = request.session.get("db_type", "relational")

    context = {
        "db_type": db_type,
        "current_db_type": db_type,
    }

    return render(request, "home.html", context)


@login_required
def game_search(request):
    # Obtener el tipo de base de datos de la sesión
    db_type = request.session.get("db_type", "relational")
    db_service = DatabaseService(db_type)

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
        results = db_service.search_games(selected_field, query)

    return render(
        request,
        "query.html",
        {
            "fields": fields,
            "results": results,
            "selected_field": selected_field,
            "query": query,
            "db_type": db_type,
            "current_db_type": db_type,
            "query_time": db_service.get_last_query_time(),
        },
    )


def all(request):
    # Marcar el tiempo de inicio de la vista
    start_time = time.perf_counter()

    # Obtener el tipo de base de datos de la sesión
    db_type = request.session.get("db_type", "relational")
    db_service = DatabaseService(db_type)

    # Obtener géneros
    all_genres = db_service.get_all_genres()

    # Obtener filtros
    genre_filter = request.GET.get("genre_filter", "")
    letter_filter = request.GET.get("letter_filter", "").upper()
    page = request.GET.get("page", 1)

    try:
        page = int(page)
    except ValueError:
        page = 1

    # Obtener juegos con paginación
    page_data = db_service.get_all_games(
        page=page,
        per_page=10,
        genre_filter=genre_filter if genre_filter else None,
        letter_filter=letter_filter if letter_filter else None,
    )

    # Calcular el tiempo total de la vista
    end_time = time.perf_counter()
    total_response_time = round((end_time - start_time) * 1000, 3)

    context = {
        "games": page_data["games"],
        "letter_filter": letter_filter,
        "all_genres": all_genres,
        "genre_filter": genre_filter,
        "db_type": db_type,
        "page_obj": page_data,
        "current_db_type": db_type,
        "total_response_time": total_response_time,
    }

    return render(request, "all.html", context)


@login_required
def graphs_home(request):
    db_type = request.session.get("db_type", "relational")
    return render(request, "graphs_home.html", {"db_type": db_type})


@login_required
def switch_database(request):
    """Vista para cambiar el tipo de base de datos"""
    if request.method == "POST":
        db_type = request.POST.get("db_type", "relational")
        if db_type in ["relational", "mongodb"]:
            request.session["db_type"] = db_type
            if db_type == "mongodb":
                messages.success(request, "Cambiado a MongoDB")
            else:
                messages.success(request, "Cambiado a Base de Datos Relacional")
        else:
            messages.error(request, "Tipo de base de datos no válido")

    return redirect("home")


@login_required
def database_status(request):
    """Vista para mostrar el estado de las bases de datos"""
    # Verificar estado de MongoDB
    from .mongodb_service import MongoDBService

    mongo_service = MongoDBService()
    mongo_connected = mongo_service.connect()
    mongo_count = 0

    if mongo_connected:
        mongo_service.disconnect()  # Cerrar la conexión inicial
        # Usar el método específico para contar
        mongo_count = mongo_service.count_games()

    # Verificar estado de la BD relacional
    relational_count = 0
    relational_connected = False
    try:
        relational_count = Games.objects.count()
        relational_connected = True
    except:
        relational_connected = False

    current_db = request.session.get("db_type", "relational")

    context = {
        "current_db": current_db,
        "mongo_connected": mongo_connected,
        "mongo_count": mongo_count,
        "relational_connected": relational_connected,
        "relational_count": relational_count,
    }

    return render(request, "database_status.html", context)


def graphs_by_gender(request):
    # Marcar el tiempo de inicio de la vista
    start_time = time.perf_counter()

    # Obtener el tipo de base de datos de la sesión
    db_type = request.session.get("db_type", "relational")
    db_service = DatabaseService(db_type)

    # Obtener estadísticas de géneros
    genre_stats = db_service.get_genre_statistics()

    # Calcular el tiempo total de la vista
    end_time = time.perf_counter()
    total_response_time = round((end_time - start_time) * 1000, 3)

    return render(
        request,
        "graphs_by_gender.html",
        {
            "labels": genre_stats["labels"],
            "data": genre_stats["data"],
            "db_type": db_type,
            "total_response_time": total_response_time,
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
            elif hasattr(field, "attname") and not isinstance(
                field, (models.ForeignKey, models.ManyToManyField)
            ):
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
