"""
Vistas para visualización del schema de base de datos
Principio: Single Responsibility - Solo maneja vistas de schema
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from ...services.admin import SchemaService


@login_required
def view_db_schema(request):
    """Vista para mostrar schema de la base de datos"""
    models_info = SchemaService.get_models_info()
    svg_height = (len(models_info) + 1) * 120

    context = {"models_info": models_info, "svg_height": svg_height}

    return render(request, "db_schema.html", context)
