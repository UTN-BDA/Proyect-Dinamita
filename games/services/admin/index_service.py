"""
Servicio de gestión de índices de base de datos
Principio: Single Responsibility - Solo maneja índices
"""

from django.db import connection, transaction
from typing import List, Dict, Optional
from .security_service import SecurityService


class IndexService:
    """Maneja operaciones de índices de la base de datos"""

    @staticmethod
    def get_table_columns(table_name: str) -> List[str]:
        """Obtiene columnas de una tabla específica"""
        if not SecurityService.validate_table_name(table_name):
            raise ValueError(f"Tabla '{table_name}' no permitida")

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position
                """,
                ["steam", table_name],
            )
            return [row[0] for row in cursor.fetchall()]

    @staticmethod
    def get_table_indexes(table_name: str) -> List[Dict]:
        """Obtiene índices existentes de una tabla"""
        if not SecurityService.validate_table_name(table_name):
            raise ValueError(f"Tabla '{table_name}' no permitida")

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    indexname,
                    indexdef,
                    COALESCE(pg_size_pretty(pg_relation_size(indexname::regclass)), 'N/A') as size
                FROM pg_indexes 
                WHERE schemaname = %s AND tablename = %s
                ORDER BY indexname
                """,
                ["steam", table_name],
            )

            return [
                {"name": row[0], "definition": row[1], "size": row[2]}
                for row in cursor.fetchall()
            ]

    @staticmethod
    def create_index(
        table_name: str, column_name: str, index_type: str = "BTREE"
    ) -> Dict[str, any]:
        """Crea un índice en una tabla"""

        # Validaciones de seguridad
        if not SecurityService.validate_table_name(table_name):
            raise ValueError(f"Tabla '{table_name}' no permitida")

        if not SecurityService.validate_index_type(index_type):
            raise ValueError(f"Tipo de índice '{index_type}' no permitido")

        # Generar nombre del índice
        index_name = f"idx_{table_name}_{column_name}_{index_type.lower()}"

        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    # Verificar si ya existe
                    if IndexService._index_exists(index_name):
                        return {
                            "success": False,
                            "message": f"El índice '{index_name}' ya existe",
                        }

                    # Crear índice
                    sql = f"""
                        CREATE INDEX "{index_name}" 
                        ON "steam"."{table_name}" 
                        USING {index_type} ("{column_name}")
                    """
                    cursor.execute(sql)

                    # Obtener tamaño del índice
                    cursor.execute(
                        "SELECT pg_size_pretty(pg_relation_size(%s));", [index_name]
                    )
                    size_result = cursor.fetchone()
                    index_size = size_result[0] if size_result else "No disponible"

                    return {
                        "success": True,
                        "message": f"Índice '{index_name}' creado. Tamaño: {index_size}",
                        "index_name": index_name,
                    }

        except Exception as e:
            return {"success": False, "message": f"Error al crear índice: {str(e)}"}

    @staticmethod
    def drop_index(index_name: str) -> Dict[str, any]:
        """Elimina un índice específico"""

        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    # Verificar si existe
                    if not IndexService._index_exists(index_name):
                        return {
                            "success": False,
                            "message": f"El índice '{index_name}' no existe",
                        }

                    # Eliminar índice
                    cursor.execute(f'DROP INDEX IF EXISTS "{index_name}";')

                    return {
                        "success": True,
                        "message": f"Índice '{index_name}' eliminado correctamente",
                    }

        except Exception as e:
            return {"success": False, "message": f"Error al eliminar índice: {str(e)}"}

    @staticmethod
    def drop_all_table_indexes(table_name: str) -> Dict[str, any]:
        """Elimina todos los índices de una tabla (excepto automáticos)"""
        if not SecurityService.validate_table_name(table_name):
            raise ValueError(f"Tabla '{table_name}' no permitida")

        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    # Obtener índices no automáticos
                    cursor.execute(
                        """
                        SELECT indexname, indexdef
                        FROM pg_indexes 
                        WHERE schemaname = %s AND tablename = %s
                        AND indexname NOT LIKE '%%_pkey'
                        AND indexname NOT LIKE '%%_key'
                        """,
                        ["steam", table_name],
                    )

                    all_indices = cursor.fetchall()
                    dropped_count = 0

                    for index_name, index_def in all_indices:
                        cursor.execute(f'DROP INDEX IF EXISTS "{index_name}";')
                        dropped_count += 1

                    return {
                        "success": True,
                        "message": f"Se eliminaron {dropped_count} índices de la tabla '{table_name}'",
                    }

        except Exception as e:
            return {"success": False, "message": f"Error al eliminar índices: {str(e)}"}

    @staticmethod
    def _index_exists(index_name: str) -> bool:
        """Verifica si un índice existe"""
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1 FROM pg_indexes 
                    WHERE indexname = %s
                )
                """,
                [index_name],
            )
            result = cursor.fetchone()
            return result[0] if result else False
