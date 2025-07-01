"""
Configuración específica para los tests
"""

import os
import tempfile
from .settings import *

# Base de datos en memoria para tests más rápidos
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}


# Desactivar migraciones para acelerar tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Configuración para tests de MongoDB
MONGO_URI_TEST = "mongodb://localhost:27017/"
MONGO_DB_NAME_TEST = "test_steam_games_db"

# Logging simplificado para tests
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}

# Cache en memoria para tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Password hashers más rápidos para tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Media files en directorio temporal
MEDIA_ROOT = tempfile.mkdtemp()

# Desactivar debug para tests
DEBUG = False
TEMPLATE_DEBUG = False
