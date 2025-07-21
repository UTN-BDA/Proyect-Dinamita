"""
Comando de gestión para restaurar backups de la base de datos Steam desde la línea de comandos.

Uso:
    python manage.py restore_steam backup_file.sql
    python manage.py restore_steam backup_file.sql --truncate
    python manage.py restore_steam backup_file.sql --dry-run
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import subprocess
import os
import tempfile
import re


class Command(BaseCommand):
    help = "Restaurar backup de la base de datos Steam"

    def add_arguments(self, parser):
        parser.add_argument(
            "backup_file", type=str, help="Ruta del archivo de backup SQL"
        )
        parser.add_argument(
            "--truncate",
            action="store_true",
            help="Limpiar tablas antes de restaurar (TRUNCATE)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Solo mostrar qué se haría, sin ejecutar",
        )
        parser.add_argument(
            "--force", action="store_true", help="No pedir confirmación"
        )

    def handle(self, *args, **options):
        backup_file = options["backup_file"]

        # Verificar que el archivo existe
        if not os.path.exists(backup_file):
            raise CommandError(f"Archivo no encontrado: {backup_file}")

        if not backup_file.endswith(".sql"):
            raise CommandError("El archivo debe tener extensión .sql")

        # Leer y analizar el archivo
        try:
            with open(backup_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            raise CommandError(f"Error al leer el archivo: {e}")

        # Extraer información del backup
        tables_in_backup = self.extract_tables_from_backup(content)
        metadata = self.extract_metadata_from_backup(content)

        # Mostrar información del backup
        self.stdout.write(self.style.SUCCESS("📄 Información del Backup:"))
        if metadata:
            for key, value in metadata.items():
                self.stdout.write(f"   {key}: {value}")

        if tables_in_backup:
            self.stdout.write(f"   Tablas encontradas: {', '.join(tables_in_backup)}")
        else:
            self.stdout.write(
                self.style.WARNING("   ⚠️  No se pudieron detectar tablas específicas")
            )

        file_size = os.path.getsize(backup_file)
        self.stdout.write(f"   Tamaño del archivo: {file_size:,} bytes")

        # Modo dry-run
        if options["dry_run"]:
            self.stdout.write(
                self.style.WARNING(
                    "\n🔍 MODO DRY-RUN - No se ejecutarán cambios reales"
                )
            )

            if options["truncate"] and tables_in_backup:
                self.stdout.write("   Se ejecutarían los siguientes TRUNCATE:")
                for table in tables_in_backup:
                    self.stdout.write(
                        f"     TRUNCATE TABLE steam.{table} RESTART IDENTITY CASCADE;"
                    )

            self.stdout.write("   Se ejecutaría el restore del archivo SQL")
            self.stdout.write("\nPara ejecutar realmente, remove --dry-run")
            return

        # Pedir confirmación si no se forzó
        if not options["force"]:
            self.stdout.write(
                self.style.WARNING(
                    "\n⚠️  ATENCIÓN: Esta operación modificará la base de datos"
                )
            )

            if options["truncate"]:
                self.stdout.write(
                    self.style.ERROR(
                        "   Se ELIMINARÁN todos los datos de las tablas afectadas"
                    )
                )

            response = input("\n¿Continuar? [y/N]: ")
            if response.lower() not in ["y", "yes", "sí", "si"]:
                self.stdout.write("Operación cancelada")
                return

        # Configuración de la base de datos
        db = settings.DATABASES["default"]
        env = os.environ.copy()
        env["PGPASSWORD"] = db["PASSWORD"]

        try:
            # Truncar tablas si se solicitó
            if options["truncate"] and tables_in_backup:
                self.stdout.write("\n🗑️  Limpiando tablas...")

                truncate_commands = []
                for table in tables_in_backup:
                    truncate_commands.append(
                        f"TRUNCATE TABLE steam.{table} RESTART IDENTITY CASCADE;"
                    )

                # Crear archivo temporal para los comandos TRUNCATE
                truncate_sql = "\n".join(truncate_commands)
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".sql", delete=False
                ) as temp_file:
                    temp_file.write(truncate_sql)
                    truncate_file_path = temp_file.name

                truncate_cmd = [
                    "psql",
                    "-h",
                    db["HOST"],
                    "-U",
                    db["USER"],
                    "-d",
                    db["NAME"],
                    "-f",
                    truncate_file_path,
                ]

                result = subprocess.run(
                    truncate_cmd, check=True, env=env, capture_output=True, text=True
                )

                os.unlink(truncate_file_path)  # Limpiar archivo temporal
                self.stdout.write("   ✅ Tablas limpiadas exitosamente")

            # Ejecutar el restore
            self.stdout.write("\n📥 Restaurando datos...")

            cmd = [
                "psql",
                "-h",
                db["HOST"],
                "-U",
                db["USER"],
                "-d",
                db["NAME"],
                "-f",
                backup_file,
                "-v",
                "ON_ERROR_STOP=1",
            ]

            result = subprocess.run(
                cmd, check=True, env=env, capture_output=True, text=True
            )

            self.stdout.write(
                self.style.SUCCESS("✅ Restauración completada exitosamente")
            )

            # Mostrar resumen
            if result.stdout:
                # Contar líneas procesadas (aproximado)
                lines_processed = len(
                    [line for line in result.stdout.split("\n") if line.strip()]
                )
                if lines_processed > 0:
                    self.stdout.write(f"   Líneas procesadas: {lines_processed}")

        except subprocess.CalledProcessError as e:
            error_msg = (
                f"Error durante la restauración: {e.stderr if e.stderr else str(e)}"
            )
            raise CommandError(error_msg)
        except Exception as e:
            raise CommandError(f"Error inesperado: {str(e)}")

    def extract_tables_from_backup(self, content):
        """Extraer nombres de tablas del contenido del backup"""
        # Buscar patrones COPY steam.tabla_name
        table_pattern = r"COPY steam\.(\w+)"
        tables = re.findall(table_pattern, content)
        return sorted(list(set(tables)))  # Eliminar duplicados y ordenar

    def extract_metadata_from_backup(self, content):
        """Extraer metadatos del archivo de backup"""
        metadata = {}
        lines = content.split("\n")[:20]  # Solo revisar las primeras 20 líneas

        for line in lines:
            if line.startswith("-- Backup creado el:"):
                metadata["Fecha de creación"] = line.replace(
                    "-- Backup creado el:", ""
                ).strip()
            elif line.startswith("-- Tablas incluidas:"):
                metadata["Tablas incluidas"] = line.replace(
                    "-- Tablas incluidas:", ""
                ).strip()
            elif line.startswith("-- Incluye datos:"):
                metadata["Incluye datos"] = line.replace(
                    "-- Incluye datos:", ""
                ).strip()
            elif line.startswith("-- Esquema:"):
                metadata["Esquema"] = line.replace("-- Esquema:", "").strip()
            elif line.startswith("-- Comando utilizado:"):
                metadata["Comando utilizado"] = line.replace(
                    "-- Comando utilizado:", ""
                ).strip()

        return metadata
