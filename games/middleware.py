import time
from django.utils.deprecation import MiddlewareMixin


class QueryTimeMiddleware(MiddlewareMixin):
    """Middleware para medir el tiempo total de respuesta de las páginas"""

    def process_request(self, request):
        """Marcar el tiempo de inicio de la request"""
        request.start_time = time.time()

    def process_template_response(self, request, response):
        """Calcular el tiempo antes de renderizar el template"""
        if hasattr(request, "start_time"):
            total_time = time.time() - request.start_time
            request.total_response_time = round(total_time * 1000, 2)  # en milisegundos

            # Agregar al contexto del template si existe
            if hasattr(response, "context_data") and response.context_data:
                response.context_data["total_response_time"] = (
                    request.total_response_time
                )
                response.context_data["current_db_type"] = request.session.get(
                    "db_type", "relational"
                )

        return response

    def process_response(self, request, response):
        """Agregar header con el tiempo de respuesta"""
        if hasattr(request, "total_response_time"):
            # Actualizar el tiempo final
            if hasattr(request, "start_time"):
                total_time = time.time() - request.start_time
                request.total_response_time = round(total_time * 1000, 2)

            # Agregar header con el tiempo de respuesta
            response["X-Response-Time"] = f"{request.total_response_time}ms"

        return response
