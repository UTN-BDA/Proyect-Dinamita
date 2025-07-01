from django import template

register = template.Library()


@register.filter
def format_query_time(value):
    """Formatear el tiempo de consulta para mostrar de manera más legible"""
    if value is None or value == "" or value == 0:
        return ""

    try:
        # Convertir a float si es string
        if isinstance(value, str):
            value = float(value)

        # El valor ya viene en milisegundos desde el middleware
        if value < 1:
            return f"{value:.2f} ms (instantáneo)"
        elif value < 50:
            return f"{value:.2f} ms (muy rápido)"
        elif value < 200:
            return f"{value:.2f} ms (rápido)"
        elif value < 500:
            return f"{value:.2f} ms (normal)"
        elif value < 1000:
            return f"{value:.2f} ms (lento)"
        else:
            return f"{value:.2f} ms (muy lento)"
    except (ValueError, TypeError):
        return ""


@register.inclusion_tag("query_time_display.html")
def show_query_time(
    query_time=None, db_type=None, total_response_time=None, view_processing_time=None
):
    """Template tag para mostrar el tiempo de consulta y procesamiento con estilo"""
    return {
        "query_time": query_time,
        "db_type": db_type or "relational",
        "total_response_time": total_response_time,
        "view_processing_time": view_processing_time,
    }
