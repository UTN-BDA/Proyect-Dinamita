
from .auth_views import registrar_usuario, home, graphs_home

from .game_views import (
    game_management_home,
    create_game,
    search_and_edit_game,
    edit_game,
    complete_description,
)

from .search_views import (
    game_search,
    all_games as all,  
    game_details_ajax,
)

from .analytics_views import graphs_by_gender, genre_performance_report

from .admin_views import (
    backup_db,
    restore_db,
    backup_management,
    backup_help,
    view_db_schema,
    index_management,
)

__all__ = [
    "registrar_usuario",
    "home",
    "graphs_home",
    "game_management_home",
    "create_game",
    "search_and_edit_game",
    "edit_game",
    "complete_description",
    "game_search",
    "all",
    "game_details_ajax",
    "graphs_by_gender",
    "genre_performance_report",
    "backup_db",
    "restore_db",
    "backup_management",
    "backup_help",
    "view_db_schema",
    "index_management",
]
