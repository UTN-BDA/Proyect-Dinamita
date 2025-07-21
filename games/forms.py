from django import forms
from .models import Games, AboutGame, Genres, Categories, Developers, Publishers


class GameForm(forms.ModelForm):
    """Formulario para crear/editar juegos básicos"""

    class Meta:
        model = Games
        fields = [
            "app_id",
            "name",
            "rel_date",
            "req_age",
            "price",
            "dlc_count",
            "achievements",
            "estimated_owners",
        ]
        widgets = {
            "app_id": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "ID de la aplicación"}
            ),
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre del juego"}
            ),
            "rel_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "req_age": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Edad requerida"}
            ),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Precio", "step": "0.01"}
            ),
            "dlc_count": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Cantidad de DLCs"}
            ),
            "achievements": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Logros"}
            ),
            "estimated_owners": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Propietarios estimados"}
            ),
        }
        labels = {
            "app_id": "ID de la Aplicación",
            "name": "Nombre del Juego",
            "rel_date": "Fecha de Lanzamiento",
            "req_age": "Edad Requerida",
            "price": "Precio",
            "dlc_count": "Cantidad de DLCs",
            "achievements": "Logros",
            "estimated_owners": "Propietarios Estimados",
        }


class AboutGameForm(forms.ModelForm):
    """Formulario para gestionar descripciones de juegos"""

    class Meta:
        model = AboutGame
        fields = ["detailed_description", "about_the_game", "short_description"]
        widgets = {
            "detailed_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Descripción detallada",
                    "rows": 5,
                }
            ),
            "about_the_game": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Acerca del juego",
                    "rows": 4,
                }
            ),
            "short_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Descripción corta",
                    "rows": 3,
                }
            ),
        }
        labels = {
            "detailed_description": "Descripción Detallada",
            "about_the_game": "Acerca del Juego",
            "short_description": "Descripción Corta",
        }


class GameSearchForm(forms.Form):
    """Formulario para buscar juegos existentes"""

    SEARCH_FIELDS = [
        ("app_id", "ID de la Aplicación"),
        ("name", "Nombre"),
    ]

    search_field = forms.ChoiceField(
        choices=SEARCH_FIELDS,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Buscar por",
    )
    search_query = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ingrese el término de búsqueda",
            }
        ),
        label="Término de búsqueda",
    )


class GenreManagementForm(forms.Form):
    """Formulario para gestionar géneros de un juego"""

    genres = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ingrese géneros separados por comas",
            }
        ),
        label="Géneros",
        help_text="Separe los géneros con comas (ej: Acción, Aventura, RPG)",
    )
