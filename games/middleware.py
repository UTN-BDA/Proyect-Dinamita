import time
from django.utils.deprecation import MiddlewareMixin


class QueryTimeMiddleware(MiddlewareMixin):
    """Middleware para medir el tiempo total de respuesta de las páginas"""

    def process_request(self, request):
        """Marcar el tiempo de inicio de la request"""
        request.start_time = time.perf_counter()

    def process_response(self, request, response):
        """Agregar header con el tiempo de respuesta"""
        if hasattr(request, "start_time"):
            # Calcular tiempo total
            total_time = time.perf_counter() - request.start_time
            final_response_time = round(total_time * 1000, 3)

            # Agregar header con el tiempo de respuesta
            response["X-Response-Time"] = f"{final_response_time}ms"

            # Guardar en el request para que las vistas lo puedan usar
            request.total_response_time = final_response_time

        return response
