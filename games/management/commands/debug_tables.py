"""
Comando para debuggear las tablas disponibles para backup
"""

from django.core.management.base import BaseCommand
from django.apps import apps
from games.views.admin_views import DatabaseSchemaService


class Command(BaseCommand):
    help = "Muestra las tablas disponibles para backup"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=== TABLAS DISPONIBLES PARA BACKUP ==="))

        # Obtener tablas usando el método corregido
        available_tables = DatabaseSchemaService.get_available_tables()

        self.stdout.write(f"Total de tablas encontradas: {len(available_tables)}")
        self.stdout.write("")

        for table in available_tables:
            self.stdout.write(f"  Modelo: {table['model_name']}")
            self.stdout.write(f"  Tabla:  {table['db_table']}")
            self.stdout.write("  ---")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=== VERIFICACIÓN COMPLETA ==="))
