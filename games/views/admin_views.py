import os
import subprocess
import re
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.apps import apps
from django.db import models, connection
from django.views.decorators.http import require_http_methods


class DatabaseBackupService:
    @staticmethod
    def create_backup():
        """Crea backup completo de la base de datos"""
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

        subprocess.run(cmd, check=True, env=env)
        return backup_path, backup_file

    @staticmethod
    def create_selective_backup(selected_tables, backup_name=None, include_data=True):
        """Crea backup selectivo de tablas específicas"""
        if not backup_name:
            timestamp = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"steamdb_selective_backup_{timestamp}.sql"

        if not backup_name.endswith(".sql"):
            backup_name += ".sql"

        backup_path = os.path.join(settings.BASE_DIR, backup_name)
        db = settings.DATABASES["default"]

        # Construir comando pg_dump con tablas específicas
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
            "--schema=steam",  # Especificar el esquema steam
        ]

        # Agregar opciones según configuración
        if not include_data:
            cmd.append("--schema-only")

        # Agregar tablas específicas con el esquema correcto
        for table in selected_tables:
            # Asegurar que la tabla tenga el prefijo del esquema
            if not table.startswith("steam."):
                table_name = f"steam.{table}"
            else:
                table_name = table
            cmd.extend(["-t", table_name])

        env = os.environ.copy()
        env["PGPASSWORD"] = db["PASSWORD"]

        try:
            subprocess.run(cmd, check=True, env=env)
            return backup_path, backup_name
        except subprocess.CalledProcessError as e:
            # Mejorar el manejo de errores
            raise Exception(
                f"Error en pg_dump: {e}. Verifica que PostgreSQL esté instalado y configurado correctamente."
            )
        except Exception as e:
            raise Exception(f"Error inesperado durante el backup: {e}")

    @staticmethod
    def restore_backup(sql_file):
        """Restaura backup de la base de datos"""
        db = settings.DATABASES["default"]
        restore_path = os.path.join(settings.BASE_DIR, "restore_temp.sql")

        # Guardar archivo temporal
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

        subprocess.run(cmd, check=True, env=env)


class DatabaseSchemaService:
    """Servicio para análisis del schema - Single Responsibility"""

    @staticmethod
    def get_models_info():
        """Obtiene información de modelos permitidos - SIN TABLAS SENSIBLES"""
        models_info = []

        # Lista de tablas permitidas - SIN TABLAS DE AUTENTICACIÓN
        tablas_permitidas = [
            "about_game",
            "audio_languages",
            "developers",
            "games",
            "genres",
            "languages",
            "packages",
            "platforms",
            "publishers",
            "categories",
            "reviews",
            "playtime",
            "urls",
            "metacritic",
            "scores_and_ranks",
            # OCULTAS POR SEGURIDAD: auth_user, auth_group, auth_permission,
            # django_session, django_admin_log, django_content_type, etc.
        ]

        # Solo obtener modelos de la aplicación 'games' que estén en la lista permitida
        try:
            games_app = apps.get_app_config("games")
            for model in games_app.get_models():
                table_name = model._meta.db_table
                # SEGURIDAD: Solo incluir tablas en la lista blanca
                if table_name in tablas_permitidas:
                    model_data = DatabaseSchemaService._analyze_model(model)
                    models_info.append(model_data)
        except LookupError:
            # Fallback con lista blanca estricta
            for model in apps.get_models():
                if (
                    model._meta.app_label == "games"
                    and model._meta.db_table in tablas_permitidas
                ):
                    model_data = DatabaseSchemaService._analyze_model(model)
                    models_info.append(model_data)

        return models_info

    @staticmethod
    def _analyze_model(model):
        """Analiza un modelo específico"""
        model_name = model.__name__
        fields = []
        foreign_keys = []
        many_to_many = []

        for field in model._meta.get_fields():
            if isinstance(field, models.ForeignKey):
                foreign_keys.append(f"{field.name} → {field.related_model.__name__}")
            elif isinstance(field, models.ManyToManyField):
                many_to_many.append(f"{field.name} ↔ {field.related_model.__name__}")
            elif hasattr(field, "attname"):
                fields.append(field.attname)

        return {
            "model": model_name,
            "fields": fields,
            "foreign_keys": foreign_keys,
            "many_to_many": many_to_many,
        }

    @staticmethod
    def get_available_tables():
        """Obtiene información de tablas disponibles para backup - Con filtro de seguridad"""
        tables = []

        # Lista de tablas permitidas - SIN TABLAS DE AUTENTICACIÓN
        tablas_permitidas = [
            "about_game",
            "audio_languages",
            "developers",
            "games",
            "genres",
            "languages",
            "packages",
            "platforms",
            "publishers",
            "categories",
            "reviews",
            "playtime",
            "urls",
            "metacritic",
            "scores_and_ranks",
            # OCULTAS POR SEGURIDAD: auth_user, auth_group, auth_permission,
            # django_session, django_admin_log, django_content_type, etc.
        ]

        # Solo obtener modelos de la aplicación 'games'
        try:
            games_app = apps.get_app_config("games")
            for model in games_app.get_models():
                table_name = model._meta.db_table
                # SEGURIDAD: Solo incluir tablas en la lista blanca
                if table_name in tablas_permitidas:
                    tables.append(
                        {
                            "model_name": model.__name__,
                            "db_table": table_name,
                        }
                    )
        except LookupError:
            # Fallback con lista blanca estricta
            for model in apps.get_models():
                if (
                    model._meta.app_label == "games"
                    and model._meta.db_table in tablas_permitidas
                ):
                    tables.append(
                        {
                            "model_name": model.__name__,
                            "db_table": model._meta.db_table,
                        }
                    )
        return tables


# Vistas que usan los servicios


@login_required
def backup_db(request):
    """Vista para crear backup de la base de datos"""
    if request.method == "POST":
        try:
            # Procesar el formulario de backup
            selected_tables = request.POST.getlist("selected_tables")
            backup_name = request.POST.get("backup_name", "").strip()
            include_data = request.POST.get("include_data") == "on"

            if not selected_tables:
                messages.error(
                    request,
                    "Debes seleccionar al menos una tabla para hacer el backup.",
                )
                return redirect("backup_db")

            # Crear backup personalizado
            backup_path, backup_file = DatabaseBackupService.create_selective_backup(
                selected_tables, backup_name, include_data
            )

            # Verificar que el archivo se creó correctamente
            if not os.path.exists(backup_path) or os.path.getsize(backup_path) == 0:
                messages.error(
                    request,
                    "El backup se creó pero está vacío. Verifica que las tablas seleccionadas tengan datos.",
                )
                return redirect("backup_db")

            return FileResponse(
                open(backup_path, "rb"), as_attachment=True, filename=backup_file
            )
        except Exception as e:
            messages.error(request, f"Error al crear backup: {str(e)}")
            return redirect("backup_db")

    # GET: Mostrar formulario de selección de tablas
    available_tables = DatabaseSchemaService.get_available_tables()

    context = {
        "available_tables": available_tables,
        "current_date": __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S"),
    }

    return render(request, "backup.html", context)


@login_required
def restore_db(request):
    """Vista para restaurar base de datos"""
    if request.method == "POST" and request.FILES.get("sql_file"):
        try:
            sql_file = request.FILES["sql_file"]
            DatabaseBackupService.restore_backup(sql_file)
            messages.success(request, "Restauración completada correctamente.")
        except Exception as e:
            messages.error(request, f"Error al restaurar: {e}")

        return HttpResponseRedirect(reverse("home"))

    return render(request, "restore.html")


@login_required
def backup_management(request):
    """Vista para gestión de backups - Panel de control"""
    available_tables = DatabaseSchemaService.get_available_tables()

    context = {
        "available_tables": available_tables,
    }

    return render(request, "backup_management.html", context)


@login_required
def backup_help(request):
    """Vista para ayuda sobre backup y restore"""
    return render(request, "backup_help.html")


@login_required
def view_db_schema(request):
    """Vista para mostrar schema de la base de datos"""
    models_info = DatabaseSchemaService.get_models_info()
    svg_height = (len(models_info) + 1) * 120

    context = {"models_info": models_info, "svg_height": svg_height}

    return render(request, "db_schema.html", context)


@require_http_methods(["GET", "POST"])
@login_required
def index_management(request):
    """Vista para gestión de índices - Con tablas filtradas por seguridad"""

    mensaje = None

    # SEGURIDAD: Lista de tablas permitidas - SIN TABLAS DE AUTENTICACIÓN
    tablas_permitidas = [
        "about_game",
        "audio_languages",
        "developers",
        "games",
        "genres",
        "languages",
        "packages",
        "platforms",
        "publishers",
        "categories",
        "reviews",
        "playtime",
        "urls",
        "metacritic",
        "scores_and_ranks",
        # OCULTAS POR SEGURIDAD: auth_user, auth_group, auth_permission, django_session, etc.
    ]

    # Lista de tipos de índice permitidos
    tipos_indice_permitidos = ["BTREE", "HASH", "GIN", "GIST"]

    # Traducción de nombres
    traducciones = {
        "about_game": "Acerca del Juego",
        "audio_languages": "Idiomas de Audio",
        "developers": "Desarrolladores",
        "games": "Juegos",
        "genres": "Géneros",
        "languages": "Idiomas",
        "packages": "Paquetes",
        "platforms": "Plataformas",
        "publishers": "Distribuidores",
        "categories": "Categorías",
        "reviews": "Reseñas",
        "playtime": "Tiempo de Juego",
        "urls": "URLs",
        "metacritic": "Metacritic",
        "scores_and_ranks": "Puntuaciones y Rankings",
    }

    tablas = []
    columnas = []

    # Usar parámetros prepared statements para seguridad SQL
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
            AND table_name = ANY(%s)
            ORDER BY table_name
            """,
            ["steam", tablas_permitidas],
        )
        tablas = [row[0] for row in cursor.fetchall()]

    # Selección de tabla
    if request.method == "POST" and "tabla" in request.POST:
        tabla_sel = request.POST["tabla"]
        # Validar que la tabla esté en la lista permitida
        if tabla_sel not in tablas_permitidas:
            messages.error(request, "Tabla no disponible.")
            return redirect("index_manager")
    elif tablas:
        tabla_sel = tablas[0]
    else:
        tabla_sel = None

    if tabla_sel and tabla_sel in tablas_permitidas:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position
                """,
                ["steam", tabla_sel],
            )
            columnas = [row[0] for row in cursor.fetchall()]

        # Obtener índices existentes para la tabla seleccionada
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    indexname,
                    indexdef,
                    COALESCE(pg_size_pretty(pg_relation_size(indexname::regclass)), 'N/A') as size
                FROM
                    pg_indexes
                WHERE
                    schemaname = %s AND tablename = %s
                ORDER BY indexname
                """,
                ["steam", tabla_sel],
            )
            indices = cursor.fetchall()
            # Asegurar que cada tupla tenga exactamente 3 elementos
            indices = [
                (row[0], row[1], row[2] if len(row) > 2 else "N/A") for row in indices
            ]
    else:
        columnas = []
        indices = []

    if request.method == "POST":
        tabla = request.POST.get("tabla")
        columna = request.POST.get("columna")
        tipo = request.POST.get("tipo")
        accion = request.POST.get("accion")

        # Validaciones
        if tabla not in tablas_permitidas:
            messages.error(request, "Tabla no permitida.")
            return redirect("index_manager")

        if tipo and tipo not in tipos_indice_permitidos:
            messages.error(request, "Tipo de índice no permitido.")
            return redirect("index_manager")

        if tabla in tablas and accion in ["crear", "eliminar_todos"]:
            with connection.cursor() as cursor:
                try:
                    if accion == "crear":
                        if columna in columnas and tipo in tipos_indice_permitidos:
                            # Sanitizar nombre del índice
                            index_name = f"idx_{tabla}_{columna}_{tipo.lower()}"

                            # Verificar caracteres permitidos en nombres
                            if not re.match(r"^[a-zA-Z0-9_]+$", index_name):
                                mensaje = "Nombre de índice contiene caracteres no permitidos."
                            else:
                                # Verificar si el índice ya existe
                                cursor.execute(
                                    """
                                    SELECT indexname FROM pg_indexes 
                                    WHERE schemaname = %s AND tablename = %s AND indexname = %s
                                    """,
                                    ["steam", tabla, index_name],
                                )

                                if cursor.fetchone():
                                    mensaje = f"El índice {index_name} ya existe."
                                else:
                                    # Usar nombres escapados para CREATE INDEX
                                    try:
                                        cursor.execute(
                                            f'CREATE INDEX "{index_name}" ON "steam"."{tabla}" USING {tipo} ("{columna}");'
                                        )
                                        mensaje = f"✅ Índice {index_name} creado correctamente"
                                    except Exception as e2:
                                        mensaje = f"❌ Error al crear índice: {str(e2)}"
                        else:
                            mensaje = "Parámetros inválidos para crear índice."

                    elif accion == "eliminar_todos":
                        cursor.execute(
                            """
                            SELECT indexname, indexdef
                            FROM pg_indexes
                            WHERE schemaname = %s AND tablename = %s
                            """,
                            ["steam", tabla],
                        )
                        all_indices = cursor.fetchall()
                        eliminados = []

                        for index_name, index_def in all_indices:
                            if "PRIMARY KEY" in index_def or "UNIQUE" in index_def:
                                continue
                            # Escapar nombre del índice
                            cursor.execute(
                                f'DROP INDEX IF EXISTS "steam"."{index_name}";'
                            )
                            eliminados.append(index_name)

                        if eliminados:
                            mensaje = (
                                f"Se eliminaron los índices: {', '.join(eliminados)}"
                            )
                        else:
                            mensaje = "No hay índices eliminables (solo hay claves primarias o únicas)."

                except Exception as e:
                    mensaje = f"Error: {str(e)}"

            return HttpResponseRedirect(reverse("index_manager") + f"?tabla={tabla}")

        elif accion == "eliminar_directo":
            index_name = request.POST.get("index_name")

            # Validar que el índice pertenezca a una tabla permitida
            with connection.cursor() as cursor:
                try:
                    # Verificar que el índice existe y pertenece a una tabla permitida
                    cursor.execute(
                        """
                        SELECT tablename FROM pg_indexes 
                        WHERE schemaname = %s AND indexname = %s AND tablename = ANY(%s)
                        """,
                        ["steam", index_name, tablas_permitidas],
                    )

                    if cursor.fetchone():
                        cursor.execute(f'DROP INDEX IF EXISTS "steam"."{index_name}";')
                        mensaje = f"Índice {index_name} eliminado correctamente."
                    else:
                        mensaje = "Índice no encontrado o no permitido."

                except Exception as e:
                    mensaje = f"Error: {str(e)}"

            return HttpResponseRedirect(reverse("index_manager") + f"?tabla={tabla}")

        else:
            mensaje = "Parámetros inválidos."

    tablas_traducidas = [(t, traducciones.get(t, t)) for t in tablas]
    context = {
        "tablas_traducidas": tablas_traducidas,
        "tabla": tabla_sel,
        "columnas": columnas,
        "indices": indices if tabla_sel else [],
        "mensaje": mensaje,
    }

    return render(request, "index_management.html", context)
