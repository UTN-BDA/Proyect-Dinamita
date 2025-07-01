def database_context(request):
    """Context processor para agregar información de base de datos a todos los templates"""
    context = {
        "current_db_type": request.session.get("db_type", "relational"),
    }

    # Agregar tiempo total de respuesta si está disponible
    if hasattr(request, "total_response_time"):
        context["total_response_time"] = request.total_response_time

    return context
