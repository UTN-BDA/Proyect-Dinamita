"""
Views principales - Refactorizadas aplicando principios SOLID, DRY, KISS
Las vistas se han reorganizado en una carpeta especializada para mejor modularidad
"""

# Importar todas las vistas desde la carpeta views
from .views import *

# Re-exportar automáticamente todas las vistas del paquete views
# Esto mantiene la compatibilidad total con las URLs existentes
