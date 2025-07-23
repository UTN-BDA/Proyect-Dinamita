"""
Vistas de análisis especializadas
Principio SOLID: Interface Segregation
"""

from games.views.analytics.genre_views import graphs_by_gender, genre_performance_report

__all__ = ["graphs_by_gender", "genre_performance_report"]
