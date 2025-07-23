"""
Vistas para gestión de índices de base de datos
Principio: Single Responsibility - Solo maneja vistas de índices
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from ...services.admin import IndexService, SchemaService, SecurityService


@require_http_methods(["GET", "POST"])
@login_required
def index_management(request):
    """Vista para gestión de índices"""

    # Obtener tablas disponibles
    available_tables = SchemaService.get_available_tables()
    table_translations = SchemaService.get_table_translations()

    # Variables de contexto
    mensaje = None
    tabla_sel = None
    columnas = []
    indices = []

    # Selección de tabla
    if request.method == "POST" and "tabla" in request.POST:
        tabla_sel = request.POST["tabla"]
        if not SecurityService.validate_table_name(tabla_sel):
            messages.error(request, "Tabla no permitida")
            tabla_sel = None
    elif available_tables:
        tabla_sel = available_tables[0]["db_table"]

    # Obtener columnas e índices si hay tabla seleccionada
    if tabla_sel:
        try:
            columnas = IndexService.get_table_columns(tabla_sel)
            indices = IndexService.get_table_indexes(tabla_sel)
        except Exception as e:
            messages.error(request, f"Error al obtener información: {str(e)}")

    # Procesar acciones de índices
    if request.method == "POST":
        resultado = _process_index_action(request, tabla_sel)
        if resultado:
            mensaje = resultado

    # Preparar contexto
    tablas_traducidas = [
        (
            table["db_table"],
            table_translations.get(table["db_table"], table["db_table"]),
        )
        for table in available_tables
    ]

    context = {
        "tablas_traducidas": tablas_traducidas,
        "tabla": tabla_sel,
        "columnas": columnas,
        "indices": indices,
        "mensaje": mensaje,
    }

    return render(request, "index_management.html", context)


def _process_index_action(request, tabla_sel: str) -> str:
    """Procesa acciones sobre índices"""
    if not tabla_sel:
        return "Debe seleccionar una tabla válida"

    accion = request.POST.get("accion")

    try:
        if accion == "crear":
            return _handle_create_index(request, tabla_sel)
        elif accion == "eliminar_todos":
            return _handle_drop_all_indexes(tabla_sel)
        elif accion == "eliminar_directo":
            return _handle_drop_specific_index(request)
        else:
            return "Acción no válida"

    except Exception as e:
        return f"Error: {str(e)}"


def _handle_create_index(request, tabla_sel: str) -> str:
    """Maneja creación de índice"""
    columna = request.POST.get("columna")
    tipo = request.POST.get("tipo", "BTREE")

    if not columna:
        return "Debe seleccionar una columna"

    if not SecurityService.validate_index_type(tipo):
        return "Tipo de índice no permitido"

    resultado = IndexService.create_index(tabla_sel, columna, tipo)

    if resultado["success"]:
        return f"✅ {resultado['message']}"
    else:
        return f"❌ {resultado['message']}"


def _handle_drop_all_indexes(tabla_sel: str) -> str:
    """Maneja eliminación de todos los índices"""
    resultado = IndexService.drop_all_table_indexes(tabla_sel)

    if resultado["success"]:
        return f"✅ {resultado['message']}"
    else:
        return f"❌ {resultado['message']}"


def _handle_drop_specific_index(request) -> str:
    """Maneja eliminación de índice específico"""
    index_name = request.POST.get("index_name")

    if not index_name:
        return "Debe especificar el nombre del índice"

    resultado = IndexService.drop_index(index_name)

    if resultado["success"]:
        return f"✅ {resultado['message']}"
    else:
        return f"❌ {resultado['message']}"
