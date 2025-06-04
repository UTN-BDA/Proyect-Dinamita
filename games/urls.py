from django.urls import path, include
from .views import game_search
from django.contrib.auth import views as auth_views
from .views import registrar_usuario

urlpatterns = [
    path("search/", game_search, name="game_search"),
    path("register/", registrar_usuario, name="register"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
