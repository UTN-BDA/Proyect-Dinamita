import time
from functools import wraps
from django.shortcuts import render


def measure_page_time(template_name):
    """
    Decorador para medir automáticamente el tiempo de carga de una página
    y pasarlo al contexto del template.
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Marcar tiempo de inicio de la vista
            start_time = time.perf_counter()

            # Ejecutar la vista original
            result = view_func(request, *args, **kwargs)

            # Calcular tiempo transcurrido
            end_time = time.perf_counter()
            total_time = round((end_time - start_time) * 1000, 3)

            # Si la vista devolvió un contexto y template, agregamos el tiempo
            if hasattr(result, "context_data") and result.context_data:
                result.context_data["total_response_time"] = total_time
                if "current_db_type" not in result.context_data:
                    result.context_data["current_db_type"] = request.session.get(
                        "db_type", "relational"
                    )

            # Si la vista devolvió un render(), tenemos que crear uno nuevo con el contexto actualizado
            elif isinstance(result, type(render(request, template_name, {}))):
                # Para el caso de render() necesitamos extraer el contexto y agregarlo
                context = getattr(result, "context_data", {})
                context["total_response_time"] = total_time
                if "current_db_type" not in context:
                    context["current_db_type"] = request.session.get(
                        "db_type", "relational"
                    )

                # Si es un HttpResponse normal, no podemos modificar el contexto
                # En este caso, guardamos el tiempo en el request para que el middleware lo use
                request.page_load_time = total_time

            return result

        return wrapper

    return decorator


def add_timing_context(view_func):
    """
    Decorador más simple que solo agrega el tiempo al request
    para que las vistas puedan acceder a él
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        start_time = time.perf_counter()

        # Ejecutar la vista
        result = view_func(request, *args, **kwargs)

        # Calcular tiempo y guardarlo en request
        end_time = time.perf_counter()
        request.view_execution_time = round((end_time - start_time) * 1000, 3)

        return result

    return wrapper
