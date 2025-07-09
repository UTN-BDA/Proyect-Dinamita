from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError

from ..handlers import FormHandler, GameFormProcessor, SearchHandler, GenreProcessor
from ..forms import GameForm, AboutGameForm, GameSearchForm, GenreManagementForm
from ..services import TransactionService, GameService, AboutGameService, GenreService


@login_required
def game_management_home(request):
    return render(request, "game_management/home.html")


@login_required
def create_game(request):
    if request.method == "POST":
        game_form = GameForm(request.POST)
        description_form = AboutGameForm(request.POST)
        genre_form = GenreManagementForm(request.POST)

        if game_form.is_valid():
            try:
                # Preparar datos usando el procesador
                data = GameFormProcessor.prepare_game_data(
                    {
                        "game_form": game_form,
                        "description_form": description_form,
                        "genre_form": genre_form,
                    }
                )

                # Crear juego completo
                result = TransactionService.create_complete_game(
                    data["game_data"], data["description_data"], data["genres_list"]
                )

                messages.success(
                    request, f"Juego '{result['game'].name}' creado exitosamente"
                )
                return redirect("game_management_home")

            except ValidationError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f"Error inesperado: {str(e)}")
    else:
        game_form = GameForm()
        description_form = AboutGameForm()
        genre_form = GenreManagementForm()

    return render(
        request,
        "game_management/create_game.html",
        {
            "game_form": game_form,
            "description_form": description_form,
            "genre_form": genre_form,
        },
    )


@login_required
def search_and_edit_game(request):
    """Vista para buscar juegos - Simplificada"""

    def search_callback(form_data):
        field = form_data["search_field"]
        query = form_data["search_query"]
        return GameService.search_games(field, query)

    search_form, games = SearchHandler.handle_search(
        request, GameSearchForm, search_callback
    )

    return render(
        request,
        "game_management/search_game.html",
        {
            "search_form": search_form,
            "games": games,
        },
    )


@login_required
def edit_game(request, app_id):
    """Vista para editar un juego existente - Simplificada"""

    # Verificar que el juego existe
    game = GameService.get_game(app_id)
    if not game:
        messages.error(request, f"No se encontró el juego con ID {app_id}")
        return redirect("search_and_edit_game")

    # Obtener datos existentes
    existing_description = AboutGameService.get_description(app_id)
    existing_genres = GenreService.get_game_genres(app_id)

    if request.method == "POST":
        game_form = GameForm(request.POST, instance=game)
        description_form = AboutGameForm(request.POST, instance=existing_description)
        genre_form = GenreManagementForm(request.POST)

        if game_form.is_valid():
            try:
                # Preparar datos usando el procesador
                data = GameFormProcessor.prepare_game_data(
                    {
                        "game_form": game_form,
                        "description_form": description_form,
                        "genre_form": genre_form,
                    }
                )

                # Actualizar juego completo
                TransactionService.update_complete_game(
                    app_id,
                    data["game_data"],
                    data["description_data"],
                    data["genres_list"],
                )

                messages.success(
                    request, f"Juego '{game.name}' actualizado exitosamente"
                )
                return redirect("search_and_edit_game")

            except ValidationError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f"Error inesperado: {str(e)}")
    else:
        game_form = GameForm(instance=game)
        description_form = AboutGameForm(instance=existing_description)

        # Pre-cargar géneros en el formulario
        genres_text = GenreProcessor.prepare_genres_for_form(existing_genres)
        genre_form = GenreManagementForm(initial={"genres": genres_text})

    return render(
        request,
        "game_management/edit_game.html",
        {
            "game": game,
            "game_form": game_form,
            "description_form": description_form,
            "genre_form": genre_form,
        },
    )


@login_required
def complete_description(request, app_id):
    """Vista para completar descripción - Simplificada"""

    # Verificar que el juego existe
    game = GameService.get_game(app_id)
    if not game:
        messages.error(request, f"No se encontró el juego con ID {app_id}")
        return redirect("search_and_edit_game")

    existing_description = AboutGameService.get_description(app_id)

    if request.method == "POST":
        description_form = AboutGameForm(request.POST, instance=existing_description)

        if description_form.is_valid():
            try:
                AboutGameService.update_or_create_description(
                    app_id, description_form.cleaned_data
                )
                messages.success(
                    request,
                    f"Descripción del juego '{game.name}' actualizada exitosamente",
                )
                return redirect("search_and_edit_game")

            except ValidationError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f"Error inesperado: {str(e)}")
    else:
        description_form = AboutGameForm(instance=existing_description)

    return render(
        request,
        "game_management/complete_description.html",
        {
            "game": game,
            "description_form": description_form,
        },
    )
