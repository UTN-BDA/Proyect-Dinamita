"""
Vistas para gestión de backups y restore
Principio: Single Responsibility - Solo maneja vistas de backup/restore
"""

import os
import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, HttpResponseRedirect
from django.urls import reverse

from ...services.admin import BackupService, SchemaService, SecurityService


@login_required
def backup_db(request):
    """Vista para crear backup de la base de datos"""
    if request.method == "POST":
        try:
            # Procesar formulario de backup
            selected_tables = request.POST.getlist("selected_tables")
            backup_name = request.POST.get("backup_name", "").strip()
            include_data = request.POST.get("include_data") == "on"

            if not selected_tables:
                messages.error(
                    request,
                    "Debes seleccionar al menos una tabla para hacer el backup.",
                )
                return redirect("backup_db")

            # Crear backup usando el servicio
            backup_path, backup_file = BackupService.create_selective_backup(
                selected_tables, backup_name, include_data
            )

            # Verificaciones de seguridad y integridad
            if not _validate_backup_file(backup_path):
                messages.error(
                    request,
                    "El backup se creó pero está vacío o no es válido.",
                )
                return redirect("backup_db")

            # Servir archivo para descarga
            return _serve_backup_file(backup_path, backup_file)

        except ValueError as e:
            messages.error(request, f"Error de validación: {str(e)}")
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")

        return redirect("backup_db")

    # GET: Mostrar formulario
    context = _get_backup_context()
    return render(request, "backup.html", context)


@login_required
def restore_db(request):
    """Vista para restaurar base de datos"""
    if request.method == "POST" and request.FILES.get("sql_file"):
        try:
            sql_file = request.FILES["sql_file"]

            # Validar archivo
            if not _validate_restore_file(sql_file):
                messages.error(request, "Archivo SQL inválido")
                return render(request, "restore.html")

            # Ejecutar restore
            BackupService.restore_backup(sql_file)

            messages.success(request, "Base de datos restaurada exitosamente")
            return HttpResponseRedirect(reverse("home"))

        except Exception as e:
            messages.error(request, f"Error al restaurar: {str(e)}")

    return render(request, "restore.html")


@login_required
def backup_management(request):
    """Vista para gestión de backups - Panel de control"""
    context = {
        "available_tables": SchemaService.get_available_tables(),
    }
    return render(request, "backup_management.html", context)


@login_required
def backup_help(request):
    """Vista para ayuda sobre backup y restore"""
    return render(request, "backup_help.html")


# Funciones auxiliares - Keep It Simple
def _get_backup_context() -> dict:
    """Prepara contexto para la vista de backup"""
    return {
        "available_tables": SchemaService.get_available_tables(),
        "current_date": datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
    }


def _validate_backup_file(backup_path: str) -> bool:
    """Valida que el archivo de backup sea correcto"""
    if not os.path.exists(backup_path):
        return False

    if os.path.getsize(backup_path) == 0:
        return False

    if not SecurityService.validate_file_path(backup_path):
        return False

    return True


def _validate_restore_file(sql_file) -> bool:
    """Valida archivo de restore"""
    if not sql_file.name.endswith(".sql"):
        return False

    if sql_file.size == 0:
        return False

    return True


def _serve_backup_file(backup_path: str, backup_file: str) -> FileResponse:
    """Sirve archivo de backup para descarga"""
    return FileResponse(
        open(backup_path, "rb"),
        as_attachment=True,
        filename=backup_file,
        content_type="application/sql",
    )
