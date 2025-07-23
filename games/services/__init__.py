"""
Servicios especializados del sistema
Organizado siguiendo principios SOLID
"""

# Importar servicios desde módulos especializados
from .game_service import GameService
from .about_game_service import AboutGameService  
from .genre_service import GenreService
from .transaction_service import TransactionService

# Los nuevos servicios especializados
# Ejemplo de uso:
# from games.services.admin import BackupService
# from games.services.analytics import GenreAnalyticsService

__all__ = [
    'GameService',
    'AboutGameService',
    'GenreService', 
    'TransactionService'
]
