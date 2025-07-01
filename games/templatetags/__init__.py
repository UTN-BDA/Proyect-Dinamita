from django import template

register = template.Library()


@register.filter
def format_query_time(value):
    """Formatear el tiempo de consulta para mostrar de manera más legible"""
    if value is None:
        return ""

    if value < 1:
        return f"{value:.2f} ms (muy rápido)"
    elif value < 100:
        return f"{value:.2f} ms (rápido)"
    elif value < 500:
        return f"{value:.2f} ms (normal)"
    elif value < 1000:
        return f"{value:.2f} ms (lento)"
    else:
        return f"{value:.2f} ms (muy lento)"


@register.inclusion_tag("query_time_display.html")
def show_query_time(query_time, db_type):
    """Template tag para mostrar el tiempo de consulta con estilo"""
    return {
        "query_time": query_time,
        "db_type": db_type,
        "formatted_time": format_query_time(query_time),
    }
