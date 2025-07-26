
from .admin import (
    backup_db,
    restore_db,
    backup_management,
    backup_help,
    view_db_schema,
    index_management,
)


class DatabaseBackupService:
   
    @staticmethod
    def create_backup():
        from ..services.admin import BackupService

        return BackupService.create_full_backup()

    @staticmethod
    def create_selective_backup(selected_tables, backup_name=None, include_data=True):
        from ..services.admin import BackupService

        return BackupService.create_selective_backup(
            selected_tables, backup_name, include_data
        )

    @staticmethod
    def restore_backup(sql_file):
        from ..services.admin import BackupService

        return BackupService.restore_backup(sql_file)


class DatabaseSchemaService:

    @staticmethod
    def get_models_info():
        from ..services.admin import SchemaService

        return SchemaService.get_models_info()

    @staticmethod
    def get_available_tables():
        from ..services.admin import SchemaService

        return SchemaService.get_available_tables()


