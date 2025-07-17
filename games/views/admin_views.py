"""
Vistas para administración del sistema (backup, restore, schema)
Aplicando principios SOLID - Single Responsibility y Open/Closed
"""

import os
import subprocess
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.apps import apps
from django.db import models, connection
from django.views.decorators.http import require_http_methods


class DatabaseBackupService:
    """Servicio para manejo de backups - Single Responsibility"""

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
            timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"steamdb_selective_backup_{timestamp}.sql"
        
        if not backup_name.endswith('.sql'):
            backup_name += '.sql'
            
        backup_path = os.path.join(settings.BASE_DIR, backup_name)
        db = settings.DATABASES["default"]

        # Construir comando pg_dump con tablas específicas
        cmd = [
            "pg_dump",
            "-h", db["HOST"],
            "-U", db["USER"],
            "-d", db["NAME"],
            "-f", backup_path,
        ]
        
        # Agregar opciones según configuración
        if not include_data:
            cmd.append("--schema-only")
        
        # Agregar tablas específicas
        for table in selected_tables:
            cmd.extend(["-t", table])

        env = os.environ.copy()
        env["PGPASSWORD"] = db["PASSWORD"]

        subprocess.run(cmd, check=True, env=env)
        return backup_path, backup_name

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
        """Obtiene información de todos los modelos"""
        models_info = []

        for model in apps.get_models():
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
        """Obtiene información de tablas disponibles para backup"""
        tables = []
        for model in apps.get_models():
            tables.append(
                {
                    "model_name": model.__name__,
                    "db_table": model._meta.db_table,
                }
            )
        return tables


# Vistas que usan los servicios


def backup_db(request):
    """Vista para crear backup de la base de datos"""
    if request.method == "POST":
        try:
            # Procesar el formulario de backup
            selected_tables = request.POST.getlist('selected_tables')
            backup_name = request.POST.get('backup_name', '').strip()
            include_data = request.POST.get('include_data') == 'on'
            
            if not selected_tables:
                messages.error(request, "Debes seleccionar al menos una tabla para hacer el backup.")
                return redirect('backup_db')
            
            # Crear backup personalizado
            backup_path, backup_file = DatabaseBackupService.create_selective_backup(
                selected_tables, backup_name, include_data
            )
            
            return FileResponse(
                open(backup_path, "rb"), as_attachment=True, filename=backup_file
            )
        except Exception as e:
            messages.error(request, f"Error al crear backup: {e}")
            return redirect('backup_db')
    
    # GET: Mostrar formulario de selección de tablas
    available_tables = DatabaseSchemaService.get_available_tables()
    
    context = {
        'available_tables': available_tables,
        'current_date': __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
    }
    
    return render(request, "backup.html", context)


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


def backup_management(request):
    """Vista para gestión de backups - Panel de control"""
    available_tables = DatabaseSchemaService.get_available_tables()

    context = {
        "available_tables": available_tables,
    }

    return render(request, "backup_management.html", context)


def backup_help(request):
    """Vista para ayuda sobre backup y restore"""
    return render(request, "backup_help.html")


def view_db_schema(request):
    """Vista para mostrar schema de la base de datos"""
    models_info = DatabaseSchemaService.get_models_info()
    svg_height = (len(models_info) + 1) * 120

    context = {"models_info": models_info, "svg_height": svg_height}

    return render(request, "db_schema.html", context)


@require_http_methods(["GET", "POST"])
def index_management(request):
    mensaje = None

    # Solo estas tablas permitidas
    tablas_permitidas = [
        "about_game", "audio_lenguages", "developers", "games", "genres",
        "languages", "packages", "plataforms", "publishers"
    ]
    # Traducción de nombres
    traducciones = {
        "about_game": "Acerca del Juego",
        "audio_lenguages": "Idiomas de Audio",
        "developers": "Desarrolladores",
        "games": "Juegos",
        "genres": "Géneros",
        "languages": "Idiomas",
        "packages": "Paquetes",
        "plataforms": "Plataformas",
        "publishers": "Distribuidores"
    }

    tablas = []
    columnas = []

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'steam'
        """)
        tablas = [row[0] for row in cursor.fetchall() if row[0] in tablas_permitidas]

    # Selección de tabla
    if request.method == "POST" and "tabla" in request.POST:
        tabla_sel = request.POST["tabla"]
    elif tablas:
        tabla_sel = tablas[0]
    else:
        tabla_sel = None

    if tabla_sel:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'steam' AND table_name = %s
            """, [tabla_sel])
            columnas = [row[0] for row in cursor.fetchall()]
    else:
        columnas = []

    if request.method == "POST":
        tabla = request.POST.get("tabla")
        columna = request.POST.get("columna")
        tipo = request.POST.get("tipo")
        accion = request.POST.get("accion")

        if tabla in tablas and columna in columnas and tipo in ["BTREE", "HASH", "GIN", "GIST"] and accion in ["crear", "eliminar"]:
            index_name = f"idx_{tabla}_{columna}_{tipo.lower()}"
            with connection.cursor() as cursor:
                try:
                    if accion == "crear":
                        sql = f'CREATE INDEX {index_name} ON steam."{tabla}" USING {tipo} ("{columna}");'
                        cursor.execute(sql)
                        mensaje = f"Índice {index_name} creado correctamente."
                    elif accion == "eliminar":
                        sql = f'DROP INDEX IF EXISTS {index_name};'
                        cursor.execute(sql)
                        mensaje = f"Índice {index_name} eliminado correctamente."
                except Exception as e:
                    mensaje = f"Error: {str(e)}"
        else:
            mensaje = "Parámetros inválidos."

    tablas_traducidas = [(t, traducciones.get(t, t)) for t in tablas]
    context = {
        "tablas_traducidas": tablas_traducidas,
        "tabla": tabla_sel,
        "columnas": columnas,
        "mensaje": mensaje,
    }
    return render(request, "index_management.html", context)
