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
from django.apps import apps
from datetime import datetime
import tempfile


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


@login_required
def backup_db(request):
    if request.method == "GET":
        # Obtener todos los modelos de la aplicación games
        available_tables = []
        for model in apps.get_app_config("games").get_models():
            available_tables.append(
                {"model_name": model.__name__, "db_table": model._meta.db_table}
            )

        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")

        return render(
            request,
            "backup.html",
            {"available_tables": available_tables, "current_date": current_date},
        )

    elif request.method == "POST":
        selected_tables = request.POST.getlist("selected_tables")
        backup_name = request.POST.get("backup_name", "").strip()
        include_data = request.POST.get("include_data") == "on"

        if not selected_tables:
            messages.error(
                request, "Debes seleccionar al menos una tabla para hacer el backup."
            )
            return redirect("backup_db")

        # Generar nombre del archivo si no se proporcionó
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_steamdb_{timestamp}.sql"
        elif not backup_name.endswith(".sql"):
            backup_name += ".sql"

        backup_path = os.path.join(settings.BASE_DIR, backup_name)
        db = settings.DATABASES["default"]

        try:
            # Crear backup de tablas específicas
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
                "--schema=steam",  # Especificar el schema
            ]

            # Agregar opciones según las preferencias
            if not include_data:
                cmd.append("--schema-only")

            # Agregar las tablas específicas
            for table in selected_tables:
                cmd.extend(["-t", f"steam.{table}"])

            env = os.environ.copy()
            env["PGPASSWORD"] = db["PASSWORD"]

            result = subprocess.run(
                cmd, check=True, env=env, capture_output=True, text=True
            )

            # Verificar que el archivo se creó y tiene contenido
            if os.path.exists(backup_path) and os.path.getsize(backup_path) > 0:
                # Agregar metadatos al inicio del archivo
                metadata = f"""-- Backup creado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- Tablas incluidas: {', '.join(selected_tables)}
-- Incluye datos: {'Sí' if include_data else 'No (solo estructura)'}
-- Esquema: steam

"""
                # Leer el contenido original
                with open(backup_path, "r", encoding="utf-8") as f:
                    original_content = f.read()

                # Escribir metadatos + contenido original
                with open(backup_path, "w", encoding="utf-8") as f:
                    f.write(metadata + original_content)

                response = FileResponse(
                    open(backup_path, "rb"), as_attachment=True, filename=backup_name
                )

                # Limpiar el archivo temporal después de enviarlo
                def cleanup():
                    try:
                        os.remove(backup_path)
                    except:
                        pass

                # El archivo se limpiará cuando se complete la respuesta
                response["X-Sendfile"] = backup_path
                messages.success(request, f"Backup creado exitosamente: {backup_name}")

                return response
            else:
                messages.error(
                    request,
                    "Error: El archivo de backup está vacío o no se pudo crear.",
                )
                return redirect("backup_db")

        except subprocess.CalledProcessError as e:
            error_msg = f"Error al crear backup: {e.stderr if e.stderr else str(e)}"
            messages.error(request, error_msg)
            return redirect("backup_db")
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")
            return redirect("backup_db")


@login_required
def restore_db(request):
    if request.method == "POST" and request.FILES.get("sql_file"):
        sql_file = request.FILES["sql_file"]
        truncate_tables = request.POST.get("truncate_tables") == "on"

        if not sql_file.name.endswith(".sql"):
            messages.error(request, "El archivo debe tener extensión .sql")
            return render(request, "restore.html")

        db = settings.DATABASES["default"]

        # Crear archivo temporal para el restore
        with tempfile.NamedTemporaryFile(
            mode="wb", suffix=".sql", delete=False
        ) as temp_file:
            restore_path = temp_file.name
            for chunk in sql_file.chunks():
                temp_file.write(chunk)

        try:
            env = os.environ.copy()
            env["PGPASSWORD"] = db["PASSWORD"]

            # Si se solicita truncar tablas, hacerlo primero
            if truncate_tables:
                # Leer el archivo para identificar las tablas que contiene
                with open(restore_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Buscar las tablas mencionadas en el backup
                import re

                table_pattern = r"COPY steam\.(\w+)"
                tables_in_backup = re.findall(table_pattern, content)

                if tables_in_backup:
                    # Crear comando para truncar las tablas
                    truncate_commands = []
                    for table in tables_in_backup:
                        truncate_commands.append(
                            f"TRUNCATE TABLE steam.{table} RESTART IDENTITY CASCADE;"
                        )

                    # Ejecutar truncate commands
                    truncate_sql = "\n".join(truncate_commands)
                    with tempfile.NamedTemporaryFile(
                        mode="w", suffix=".sql", delete=False
                    ) as truncate_file:
                        truncate_file.write(truncate_sql)
                        truncate_file_path = truncate_file.name

                    truncate_cmd = [
                        "psql",
                        "-h",
                        db["HOST"],
                        "-U",
                        db["USER"],
                        "-d",
                        db["NAME"],
                        "-f",
                        truncate_file_path,
                    ]

                    subprocess.run(
                        truncate_cmd, check=True, env=env, capture_output=True
                    )
                    os.unlink(truncate_file_path)  # Limpiar archivo temporal

            # Ejecutar el restore
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
                "-v",
                "ON_ERROR_STOP=1",  # Detener en caso de error
            ]

            result = subprocess.run(
                cmd, check=True, env=env, capture_output=True, text=True
            )

            # Limpiar archivo temporal
            os.unlink(restore_path)

            success_msg = "Restauración completada correctamente."
            if truncate_tables:
                success_msg += " Las tablas fueron limpiadas antes de la restauración."

            messages.success(request, success_msg)

        except subprocess.CalledProcessError as e:
            error_msg = f"Error al restaurar: {e.stderr if e.stderr else str(e)}"
            messages.error(request, error_msg)
            # Limpiar archivo temporal en caso de error
            try:
                os.unlink(restore_path)
            except:
                pass
        except Exception as e:
            messages.error(
                request, f"Error inesperado durante la restauración: {str(e)}"
            )
            # Limpiar archivo temporal en caso de error
            try:
                os.unlink(restore_path)
            except:
                pass

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


@login_required
def backup_management(request):
    """Vista para mostrar la página de gestión de backups"""
    available_tables = []
    for model in apps.get_app_config("games").get_models():
        available_tables.append(
            {"model_name": model.__name__, "db_table": model._meta.db_table}
        )

    return render(
        request, "backup_management.html", {"available_tables": available_tables}
    )


@login_required
def backup_help(request):
    """Vista para mostrar la ayuda del sistema de backup y restore"""
    return render(request, "backup_help.html")
