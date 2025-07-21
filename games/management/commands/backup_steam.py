"""
Comando de gestión para realizar backups de la base de datos Steam desde la línea de comandos.

Uso:
    python manage.py backup_steam --tables games,genres --output mi_backup.sql
    python manage.py backup_steam --all --no-data
    python manage.py backup_steam --help
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.apps import apps
import subprocess
import os
from datetime import datetime


class Command(BaseCommand):
    help = "Crear backup de tablas específicas de la base de datos Steam"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tables",
            type=str,
            help="Lista de tablas separadas por comas (ej: games,genres,developers)",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Incluir todas las tablas de la aplicación games",
        )
        parser.add_argument(
            "--output",
            type=str,
            help="Nombre del archivo de salida (default: backup_TIMESTAMP.sql)",
        )
        parser.add_argument(
            "--no-data", action="store_true", help="Solo estructura, sin datos"
        )
        parser.add_argument(
            "--list-tables",
            action="store_true",
            help="Mostrar todas las tablas disponibles y salir",
        )

    def handle(self, *args, **options):
        # Obtener todas las tablas disponibles
        available_tables = []
        for model in apps.get_app_config("games").get_models():
            available_tables.append(
                {"model_name": model.__name__, "db_table": model._meta.db_table}
            )

        # Si solo quiere listar las tablas
        if options["list_tables"]:
            self.stdout.write(self.style.SUCCESS("Tablas disponibles:"))
            for table in available_tables:
                self.stdout.write(f"  - {table['model_name']} ({table['db_table']})")
            return

        # Determinar qué tablas incluir
        if options["all"]:
            selected_tables = [table["db_table"] for table in available_tables]
            self.stdout.write(
                f"Seleccionadas todas las tablas ({len(selected_tables)} tablas)"
            )
        elif options["tables"]:
            table_names = [name.strip() for name in options["tables"].split(",")]
            available_table_names = [table["db_table"] for table in available_tables]

            selected_tables = []
            for name in table_names:
                if name in available_table_names:
                    selected_tables.append(name)
                else:
                    # Intentar buscar por nombre de modelo
                    found = False
                    for table in available_tables:
                        if table["model_name"].lower() == name.lower():
                            selected_tables.append(table["db_table"])
                            found = True
                            break

                    if not found:
                        raise CommandError(
                            f"Tabla '{name}' no encontrada. Use --list-tables para ver las disponibles."
                        )

            self.stdout.write(
                f"Seleccionadas {len(selected_tables)} tablas: {', '.join(selected_tables)}"
            )
        else:
            raise CommandError("Debe especificar --tables o --all")

        # Generar nombre del archivo
        if options["output"]:
            output_file = options["output"]
            if not output_file.endswith(".sql"):
                output_file += ".sql"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"backup_steamdb_{timestamp}.sql"

        output_path = os.path.join(settings.BASE_DIR, output_file)

        # Configuración de la base de datos
        db = settings.DATABASES["default"]

        try:
            # Construir comando pg_dump
            cmd = [
                "pg_dump",
                "-h",
                db["HOST"],
                "-U",
                db["USER"],
                "-d",
                db["NAME"],
                "-f",
                output_path,
                "--schema=steam",
            ]

            # Agregar opciones
            if options["no_data"]:
                cmd.append("--schema-only")
                self.stdout.write("Modo: Solo estructura (sin datos)")
            else:
                self.stdout.write("Modo: Estructura + datos")

            # Agregar tablas específicas
            for table in selected_tables:
                cmd.extend(["-t", f"steam.{table}"])

            # Configurar variables de entorno
            env = os.environ.copy()
            env["PGPASSWORD"] = db["PASSWORD"]

            self.stdout.write(f"Creando backup en: {output_path}")
            self.stdout.write("Ejecutando pg_dump...")

            # Ejecutar comando
            result = subprocess.run(
                cmd, check=True, env=env, capture_output=True, text=True
            )

            # Verificar que el archivo se creó
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                # Agregar metadatos al archivo
                metadata = f"""-- Backup creado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- Comando utilizado: python manage.py backup_steam
-- Tablas incluidas: {', '.join(selected_tables)}
-- Incluye datos: {'No (solo estructura)' if options['no_data'] else 'Sí'}
-- Esquema: steam

"""
                # Leer contenido original
                with open(output_path, "r", encoding="utf-8") as f:
                    original_content = f.read()

                # Escribir metadatos + contenido
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(metadata + original_content)

                file_size = os.path.getsize(output_path)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Backup creado exitosamente: {output_file} ({file_size:,} bytes)"
                    )
                )
            else:
                raise CommandError("El archivo de backup está vacío o no se pudo crear")

        except subprocess.CalledProcessError as e:
            error_msg = f"Error en pg_dump: {e.stderr if e.stderr else str(e)}"
            raise CommandError(error_msg)
        except Exception as e:
            raise CommandError(f"Error inesperado: {str(e)}")
