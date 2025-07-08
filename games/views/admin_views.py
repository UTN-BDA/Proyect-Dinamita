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
from django.db import models


class DatabaseBackupService:
    """Servicio para manejo de backups - Single Responsibility"""

    @staticmethod
    def create_backup():
        """Crea backup de la base de datos"""
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


# Vistas que usan los servicios


def backup_db(request):
    """Vista para crear backup de la base de datos"""
    try:
        backup_path, backup_file = DatabaseBackupService.create_backup()
        return FileResponse(
            open(backup_path, "rb"), as_attachment=True, filename=backup_file
        )
    except Exception as e:
        return HttpResponse(f"Error al crear backup: {e}")


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


def view_db_schema(request):
    """Vista para mostrar schema de la base de datos"""
    models_info = DatabaseSchemaService.get_models_info()
    svg_height = (len(models_info) + 1) * 120

    context = {"models_info": models_info, "svg_height": svg_height}

    return render(request, "db_schema.html", context)
