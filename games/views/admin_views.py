"""
DEPRECATED: Este archivo ha sido refactorizado siguiendo principios SOLID, DRY y KISS.

✅ MIGRACIÓN COMPLETADA:
   - Todas las vistas han sido movidas a: games.views.admin.*
   - Todos los servicios han sido movidos a: games.services.admin.*
   - El código original de 566 líneas ha sido separado en múltiples archivos de <200 líneas

📁 NUEVA ESTRUCTURA:
   games/views/admin/backup_views.py  (~80 líneas)
   games/views/admin/schema_views.py  (~25 líneas)
   games/views/admin/index_views.py   (~120 líneas)
   games/services/admin/*             (servicios especializados)

🔄 COMPATIBILIDAD TEMPORAL:
   Este archivo mantiene los imports para compatibilidad hacia atrás.
   TODO: Migrar todas las referencias en URLs y eliminar este archivo.
"""

# ═══════════════════════════════════════════════════════════════════
# IMPORTS DE COMPATIBILIDAD - NUEVA ESTRUCTURA REFACTORIZADA
# ═══════════════════════════════════════════════════════════════════

from .admin import (
    backup_db,
    restore_db,
    backup_management,
    backup_help,
    view_db_schema,
    index_management,
)

# ═══════════════════════════════════════════════════════════════════
# CLASES DEPRECATED - MANTENER SOLO PARA COMPATIBILIDAD
# ═══════════════════════════════════════════════════════════════════


class DatabaseBackupService:
    """
    ⚠️ DEPRECATED: Usar games.services.admin.BackupService

    Esta clase se mantiene temporalmente para compatibilidad.
    Todo el código real ha sido migrado a servicios especializados.
    """

    @staticmethod
    def create_backup():
        """DEPRECATED: Usar BackupService.create_full_backup()"""
        from ..services.admin import BackupService

        return BackupService.create_full_backup()

    @staticmethod
    def create_selective_backup(selected_tables, backup_name=None, include_data=True):
        """DEPRECATED: Usar BackupService.create_selective_backup()"""
        from ..services.admin import BackupService

        return BackupService.create_selective_backup(
            selected_tables, backup_name, include_data
        )

    @staticmethod
    def restore_backup(sql_file):
        """DEPRECATED: Usar BackupService.restore_backup()"""
        from ..services.admin import BackupService

        return BackupService.restore_backup(sql_file)


class DatabaseSchemaService:
    """
    ⚠️ DEPRECATED: Usar games.services.admin.SchemaService

    Esta clase se mantiene temporalmente para compatibilidad.
    Todo el código real ha sido migrado a servicios especializados.
    """

    @staticmethod
    def get_models_info():
        """DEPRECATED: Usar SchemaService.get_models_info()"""
        from ..services.admin import SchemaService

        return SchemaService.get_models_info()

    @staticmethod
    def get_available_tables():
        """DEPRECATED: Usar SchemaService.get_available_tables()"""
        from ..services.admin import SchemaService

        return SchemaService.get_available_tables()


# ═══════════════════════════════════════════════════════════════════
# NOTA IMPORTANTE PARA DESARROLLADORES
# ═══════════════════════════════════════════════════════════════════
"""
✨ LA REFACTORIZACIÓN HA SIDO COMPLETADA ✨

El código original de este archivo ha sido completamente refactorizado
siguiendo los principios SOLID, DRY y KISS:

🎯 PRINCIPIOS APLICADOS:
   S - Single Responsibility: Cada servicio tiene una responsabilidad única
   O - Open/Closed: Servicios extensibles sin modificar código existente  
   L - Liskov Substitution: Interfaces consistentes entre servicios
   I - Interface Segregation: Interfaces específicas por funcionalidad
   D - Dependency Inversion: Vistas dependen de abstracciones, no implementaciones

🔄 DRY (Don't Repeat Yourself):
   - Código duplicado eliminado y centralizado en servicios
   - Validaciones unificadas en SecurityService
   - Utilidades comunes en servicios base

💎 KISS (Keep It Simple, Stupid):
   - Archivos pequeños y enfocados (<200 líneas)
   - Funciones simples con una única responsabilidad
   - Lógica compleja dividida en pasos comprensibles

📊 RESULTADOS:
   - Archivo original: 566 líneas ❌
   - Nuevos archivos: Todos <200 líneas ✅
   - Mantenibilidad: Mejorada significativamente ✅
   - Testabilidad: Cada componente es testeable independientemente ✅
"""
