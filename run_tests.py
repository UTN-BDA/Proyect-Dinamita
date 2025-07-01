#!/usr/bin/env python
"""
Script para ejecutar tests de manera controlada
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "steam_db.test_settings")
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    # Ejecutar tests específicos
    test_labels = [
        "games.tests.MongoDBServiceTest",
        "games.tests.DatabaseServiceTest",
        "games.tests.ViewsTest",
        "games.tests.IntegrationTest",
    ]

    failures = test_runner.run_tests(test_labels)
    if failures:
        sys.exit(bool(failures))
