"""
Configuraciones y constantes centralizadas
Aplicando principio DRY - Don't Repeat Yourself
"""

# Configuración de paginación
PAGINATION_SIZE = 10

# Campos de búsqueda disponibles
SEARCH_FIELDS = [
    ("app_id", "App ID"),
    ("name", "Nombre"),
    ("release_date", "Fecha de lanzamiento"),
    ("estimated_owners", "Dueños estimados"),
    ("peak_ccu", "Peak CCU"),
    ("required_age", "Edad requerida"),
    ("price", "Precio"),
]

# Configuración de archivos de backup
BACKUP_CONFIG = {
    "default_filename": "steamdb_backup.sql",
    "temp_restore_filename": "restore_temp.sql",
}

# Mensajes de éxito y error reutilizables
MESSAGES = {
    "game_created": "Juego '{name}' creado exitosamente",
    "game_updated": "Juego '{name}' actualizado exitosamente",
    "description_updated": "Descripción del juego '{name}' actualizada exitosamente",
    "game_not_found": "No se encontró el juego con ID {app_id}",
    "backup_success": "Backup creado exitosamente",
    "restore_success": "Restauración completada correctamente",
    "unexpected_error": "Error inesperado: {error}",
}

# URLs de redirección comunes
REDIRECT_URLS = {
    "game_management": "game_management_home",
    "search_games": "search_and_edit_game",
    "home": "home",
}
