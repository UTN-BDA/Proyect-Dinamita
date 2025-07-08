from django.urls import path, include
from django.contrib.auth import views as auth_views

from .views import (
    game_search,
    home,
    all,
    graphs_home,
    graphs_by_gender,
    backup_db,
    restore_db,
    backup_management,
    backup_help,
    registrar_usuario,
    view_db_schema,
)

urlpatterns = [
    path("", home, name="home"),
    path("search/", game_search, name="game_search"),
    path("all/", all, name="all_games"),
    path("graphs/", graphs_home, name="graphs_home"),
    path("graphs-by-gender/", graphs_by_gender, name="graphs_by_gender"),
    path("register/", registrar_usuario, name="register"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("backup/", backup_db, name="backup_db"),
    path("restore/", restore_db, name="restore_db"),
    path("backup-management/", backup_management, name="backup_management"),
    path("backup-help/", backup_help, name="backup_help"),
    path("db_schema/", view_db_schema, name="db_schema"),
]
