"""
Handlers para manejar la lógica común de formularios y responses
Aplicando principios DRY y Single Responsibility
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from typing import Dict, List, Optional, Any, Callable


class FormHandler:
    """Manejador genérico de formularios aplicando DRY principle"""

    @staticmethod
    def handle_form_submission(
        request,
        forms: Dict[str, Any],
        success_callback: Callable,
        success_message: str,
        redirect_url: str,
        template_name: str,
        context: Dict = None,
    ):
        """
        Maneja la submisión de formularios de manera genérica

        Args:
            request: HttpRequest object
            forms: Dict con las clases/instancias de formularios
            success_callback: Función a ejecutar si todos los formularios son válidos
            success_message: Mensaje de éxito
            redirect_url: URL de redirección tras éxito
            template_name: Template a renderizar
            context: Contexto adicional para el template
        """
        if request.method == "POST":
            return FormHandler._handle_post_request(
                request,
                forms,
                success_callback,
                success_message,
                redirect_url,
                template_name,
                context,
            )
        else:
            return FormHandler._handle_get_request(
                request, template_name, forms, context
            )

    @staticmethod
    def _handle_post_request(
        request,
        forms,
        success_callback,
        success_message,
        redirect_url,
        template_name,
        context,
    ):
        """Maneja requests POST"""
        # Crear formularios con datos POST o ejecutar funciones lambda
        post_forms = {}
        for key, form_definition in forms.items():
            if callable(form_definition):
                post_forms[key] = form_definition()  # Ejecutar lambda/función
            else:
                post_forms[key] = form_definition(request.POST)  # Clase de formulario

        # Verificar si el formulario principal es válido
        main_form = list(post_forms.values())[0]
        if main_form.is_valid():
            try:
                # Ejecutar la lógica de negocio
                result = success_callback(post_forms)

                messages.success(request, success_message.format(**result))
                return redirect(redirect_url)

            except ValidationError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f"Error inesperado: {str(e)}")

        # Si hay errores, renderizar con los formularios que contienen errores
        render_context = {**post_forms, **(context or {})}
        return render(request, template_name, render_context)

    @staticmethod
    def _handle_get_request(request, template_name, forms, context):
        """Maneja requests GET"""
        # Crear formularios vacíos o ejecutar funciones lambda
        get_forms = {}
        for key, form_definition in forms.items():
            if callable(form_definition):
                get_forms[key] = form_definition()  # Ejecutar lambda/función
            else:
                get_forms[key] = form_definition()  # Clase de formulario sin argumentos

        render_context = {**get_forms, **(context or {})}
        return render(request, template_name, render_context)


class GenreProcessor:
    """Procesador especializado para géneros (Single Responsibility)"""

    @staticmethod
    def process_genres_from_form(genre_form) -> List[str]:
        """Procesa géneros desde formulario"""
        if genre_form.is_valid() and genre_form.cleaned_data.get("genres"):
            return [g.strip() for g in genre_form.cleaned_data["genres"].split(",")]
        return []

    @staticmethod
    def prepare_genres_for_form(genres_list: List[str]) -> str:
        """Prepara géneros para mostrar en formulario"""
        return ", ".join(genres_list) if genres_list else ""


class GameFormProcessor:
    """Procesador especializado para formularios de juegos"""

    @staticmethod
    def prepare_game_data(forms: Dict) -> Dict:
        """Prepara datos del juego desde múltiples formularios"""
        game_form = forms.get("game_form")
        description_form = forms.get("description_form")
        genre_form = forms.get("genre_form")

        game_data = game_form.cleaned_data if game_form.is_valid() else None
        description_data = (
            description_form.cleaned_data
            if description_form and description_form.is_valid()
            else None
        )
        genres_list = (
            GenreProcessor.process_genres_from_form(genre_form) if genre_form else []
        )

        return {
            "game_data": game_data,
            "description_data": description_data,
            "genres_list": genres_list,
        }


class SearchHandler:
    """Manejador especializado para búsquedas"""

    @staticmethod
    def handle_search(request, form_class, search_callback):
        """Maneja búsquedas genéricas"""
        form = form_class()
        results = []

        if request.GET:
            form = form_class(request.GET)
            if form.is_valid():
                results = search_callback(form.cleaned_data)

        return form, results


class ResponseHelper:
    """Helper para responses comunes"""

    @staticmethod
    def redirect_with_error(message: str, redirect_url: str):
        """Redirecciona con mensaje de error"""
        from django.shortcuts import redirect
        from django.contrib import messages

        messages.error(None, message)  # El request se manejará en el template
        return redirect(redirect_url)

    @staticmethod
    def simple_render(request, template_name: str, context: Dict = None):
        """Renderizado simple con contexto opcional"""
        return render(request, template_name, context or {})
