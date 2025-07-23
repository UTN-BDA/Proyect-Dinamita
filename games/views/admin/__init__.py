"""
Vistas administrativas especializadas
Siguiendo principios SOLID - Interface Segregation
"""

from games.views.admin.backup_views import (
    backup_db,
    restore_db,
    backup_management,
    backup_help,
)
from games.views.admin.schema_views import view_db_schema
from games.views.admin.index_views import index_management

__all__ = [
    "backup_db",
    "restore_db",
    "backup_management",
    "backup_help",
    "view_db_schema",
    "index_management",
]

from .backup_views import backup_db, restore_db, backup_management, backup_help
from .schema_views import view_db_schema
from .index_views import index_management

__all__ = [
    "backup_db",
    "restore_db",
    "backup_management",
    "backup_help",
    "view_db_schema",
    "index_management",
]
