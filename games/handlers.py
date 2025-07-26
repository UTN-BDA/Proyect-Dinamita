from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from typing import Dict, List, Optional, Any, Callable


class FormHandler:

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
        
        post_forms = {}
        for key, form_definition in forms.items():
            if callable(form_definition):
                post_forms[key] = form_definition()  
            else:
                post_forms[key] = form_definition(request.POST)  

        
        main_form = list(post_forms.values())[0]
        if main_form.is_valid():
            try:
                result = success_callback(post_forms)

                messages.success(request, success_message.format(**result))
                return redirect(redirect_url)

            except ValidationError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f"Error inesperado: {str(e)}")

        render_context = {**post_forms, **(context or {})}
        return render(request, template_name, render_context)

    @staticmethod
    def _handle_get_request(request, template_name, forms, context):
        get_forms = {}
        for key, form_definition in forms.items():
            if callable(form_definition):
                get_forms[key] = form_definition()  
            else:
                get_forms[key] = form_definition()  

        render_context = {**get_forms, **(context or {})}
        return render(request, template_name, render_context)


class GenreProcessor:

    @staticmethod
    def process_genres_from_form(genre_form) -> List[str]:
        if genre_form.is_valid() and genre_form.cleaned_data.get("genres"):
            return [g.strip() for g in genre_form.cleaned_data["genres"].split(",")]
        return []

    @staticmethod
    def prepare_genres_for_form(genres_list: List[str]) -> str:
        return ", ".join(genres_list) if genres_list else ""


class GameFormProcessor:

    @staticmethod
    def prepare_game_data(forms: Dict) -> Dict:
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
    @staticmethod
    def handle_search(request, form_class, search_callback):
        form = form_class()
        results = []

        if request.GET:
            form = form_class(request.GET)
            if form.is_valid():
                results = search_callback(form.cleaned_data)

        return form, results


class ResponseHelper:
    @staticmethod
    def redirect_with_error(message: str, redirect_url: str):
        from django.shortcuts import redirect
        from django.contrib import messages

        messages.error(None, message)  
        return redirect(redirect_url)

    @staticmethod
    def simple_render(request, template_name: str, context: Dict = None):
        return render(request, template_name, context or {})
