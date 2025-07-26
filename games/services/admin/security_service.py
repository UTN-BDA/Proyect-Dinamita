
import os
import string
from django.conf import settings
from typing import List


class SecurityService:
    """Maneja todas las validaciones de seguridad"""

    # Lista de tablas permitidas
    ALLOWED_TABLES = [
        "about_game",
        "audio_languages",
        "developers",
        "games",
        "genres",
        "languages",
        "packages",
        "platforms",
        "publishers",
        "categories",
        "reviews",
        "playtime",
        "urls",
        "metacritic",
        "scores_and_ranks",
    ]

    ALLOWED_INDEX_TYPES = ["BTREE", "HASH", "GIN", "GIST"]

    @staticmethod
    def validate_table_name(table_name: str) -> bool:
        """Valida que la tabla esté en la lista permitida"""
        return table_name in SecurityService.ALLOWED_TABLES

    @staticmethod
    def validate_tables_list(tables: List[str]) -> bool:
        """Valida una lista de tablas"""
        return all(SecurityService.validate_table_name(table) for table in tables)

    @staticmethod
    def validate_index_type(index_type: str) -> bool:
        """Valida tipo de índice"""
        return index_type in SecurityService.ALLOWED_INDEX_TYPES

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitiza nombre de archivo para prevenir path traversal"""
        if not filename:
            return None

        # Solo caracteres válidos
        valid_chars = f"-_.{string.ascii_letters}{string.digits}"
        sanitized = "".join(c for c in filename if c in valid_chars)

        if not sanitized:
            return None

        # Asegurar extensión .sql
        if not sanitized.endswith(".sql"):
            sanitized += ".sql"

        return sanitized

    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """Valida que el archivo esté dentro del directorio base"""
        abs_file_path = os.path.abspath(file_path)
        abs_base_dir = os.path.abspath(settings.BASE_DIR)

        return abs_file_path.startswith(abs_base_dir)

    @staticmethod
    def validate_filename_security(filename: str) -> bool:
        """Valida seguridad del nombre de archivo"""
        if not filename or not filename.endswith(".sql"):
            return False

        dangerous_patterns = ["..", "/", "\\", "|", "&", ";", "$", "`"]
        return not any(pattern in filename for pattern in dangerous_patterns)
