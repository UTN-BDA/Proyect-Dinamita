"""
Views package - Refactorizado para mejor organización
Aplicando principios SOLID - Single Responsibility y organización modular
"""

# Importar todas las vistas desde sus módulos especializados
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
    all_games as all,  # Manteniendo compatibilidad con URLs existentes
)

from .analytics_views import graphs_by_gender

from .admin_views import (
    backup_db,
    restore_db,
    backup_management,
    backup_help,
    view_db_schema,
    index_management,
)

# Re-exportar todas las vistas para mantener compatibilidad con el sistema existente
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
    "graphs_by_gender",
    "backup_db",
    "restore_db",
    "backup_management",
    "backup_help",
    "view_db_schema",
    "index_management",
]
