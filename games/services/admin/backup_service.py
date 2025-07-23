"""
Servicio de backup y restore de base de datos
Principio: Single Responsibility - Solo maneja operaciones de backup/restore
"""

import os
import subprocess
import datetime
from django.conf import settings
from typing import Tuple, List
from .security_service import SecurityService


class BackupService:
    """Maneja operaciones de backup y restore de la base de datos"""

    @staticmethod
    def create_full_backup() -> Tuple[str, str]:
        """Crea backup completo de la base de datos"""
        backup_file = "steamdb_backup.sql"
        backup_path = os.path.join(settings.BASE_DIR, backup_file)

        BackupService._execute_pg_dump(backup_path)
        return backup_path, backup_file

    @staticmethod
    def create_selective_backup(
        selected_tables: List[str], backup_name: str = None, include_data: bool = True
    ) -> Tuple[str, str]:
        """Crea backup selectivo de tablas específicas"""

        # Validar tablas por seguridad
        if not SecurityService.validate_tables_list(selected_tables):
            raise ValueError("Una o más tablas no están permitidas")

        # Generar nombre si no se proporciona
        if not backup_name:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"steamdb_selective_backup_{timestamp}.sql"

        # Sanitizar nombre
        backup_name = SecurityService.sanitize_filename(backup_name)
        if not backup_name:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"steamdb_backup_{timestamp}.sql"

        # Construir y validar ruta
        backup_path = os.path.join(settings.BASE_DIR, backup_name)
        backup_path = os.path.abspath(backup_path)

        if not SecurityService.validate_file_path(backup_path):
            raise ValueError("Ruta de backup inválida por razones de seguridad")

        # Ejecutar backup selectivo
        BackupService._execute_selective_pg_dump(
            backup_path, selected_tables, include_data
        )

        return backup_path, backup_name

    @staticmethod
    def restore_backup(sql_file) -> None:
        """Restaura backup de la base de datos"""
        restore_path = os.path.join(settings.BASE_DIR, "restore_temp.sql")

        # Guardar archivo temporal
        with open(restore_path, "wb") as f:
            for chunk in sql_file.chunks():
                f.write(chunk)

        BackupService._execute_psql(restore_path)

        # Limpiar archivo temporal
        if os.path.exists(restore_path):
            os.remove(restore_path)

    @staticmethod
    def _get_db_config() -> dict:
        """Obtiene configuración de la base de datos"""
        return settings.DATABASES["default"]

    @staticmethod
    def _get_db_env() -> dict:
        """Prepara variables de entorno para PostgreSQL"""
        db = BackupService._get_db_config()
        env = os.environ.copy()
        env["PGPASSWORD"] = db["PASSWORD"]
        return env

    @staticmethod
    def _execute_pg_dump(backup_path: str) -> None:
        """Ejecuta pg_dump para backup completo"""
        db = BackupService._get_db_config()

        cmd = [
            "pg_dump",
            "-h",
            db["HOST"],
            "-U",
            db["USER"],
            "-d",
            db["NAME"],
            "-f",
            backup_path,
        ]

        env = BackupService._get_db_env()

        try:
            subprocess.run(cmd, check=True, env=env)
        except subprocess.CalledProcessError as e:
            raise Exception(
                f"Error en pg_dump: {e}. Verifica que PostgreSQL esté instalado y configurado correctamente."
            )

    @staticmethod
    def _execute_selective_pg_dump(
        backup_path: str, tables: List[str], include_data: bool
    ) -> None:
        """Ejecuta pg_dump para backup selectivo"""
        db = BackupService._get_db_config()

        cmd = [
            "pg_dump",
            "-h",
            db["HOST"],
            "-U",
            db["USER"],
            "-d",
            db["NAME"],
            "-f",
            backup_path,
            "--schema=steam",
        ]

        if not include_data:
            cmd.append("--schema-only")

        # Agregar tablas específicas
        for table in tables:
            table_name = f"steam.{table}" if not table.startswith("steam.") else table
            cmd.extend(["-t", table_name])

        env = BackupService._get_db_env()

        try:
            subprocess.run(cmd, check=True, env=env)
        except subprocess.CalledProcessError as e:
            raise Exception(
                f"Error en pg_dump: {e}. Verifica que PostgreSQL esté instalado y configurado correctamente."
            )

    @staticmethod
    def _execute_psql(restore_path: str) -> None:
        """Ejecuta psql para restore"""
        db = BackupService._get_db_config()

        cmd = [
            "psql",
            "-h",
            db["HOST"],
            "-U",
            db["USER"],
            "-d",
            db["NAME"],
            "-f",
            restore_path,
        ]

        env = BackupService._get_db_env()
        subprocess.run(cmd, check=True, env=env)
