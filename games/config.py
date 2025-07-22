PAGINATION_SIZE = 25

SEARCH_FIELDS = [
    ("app_id", "App ID"),
    ("name", "Nombre"),
    ("release_date", "Fecha de lanzamiento"),
    ("estimated_owners", "Dueños estimados"),
    ("peak_ccu", "Peak CCU"),
    ("required_age", "Edad requerida"),
    ("price", "Precio"),
]

BACKUP_CONFIG = {
    "default_filename": "steamdb_backup.sql",
    "temp_restore_filename": "restore_temp.sql",
}

MESSAGES = {
    "game_created": "Juego '{name}' creado exitosamente",
    "game_updated": "Juego '{name}' actualizado exitosamente",
    "description_updated": "Descripción del juego '{name}' actualizada exitosamente",
    "game_not_found": "No se encontró el juego con ID {app_id}",
    "backup_success": "Backup creado exitosamente",
    "restore_success": "Restauración completada correctamente",
    "unexpected_error": "Error inesperado: {error}",
}

REDIRECT_URLS = {
    "game_management": "game_management_home",
    "search_games": "search_and_edit_game",
    "home": "home",
}
