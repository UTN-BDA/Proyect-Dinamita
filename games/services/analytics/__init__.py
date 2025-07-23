"""
Servicios de análisis y estadísticas
Principio SOLID: Single Responsibility Principle
"""

from games.services.analytics.genre_service import GenreAnalyticsService
from games.services.analytics.performance_service import PerformanceService

__all__ = ["GenreAnalyticsService", "PerformanceService"]
