from djongo import models
import json


class GameDocument(models.Model):
    """Modelo para MongoDB que representa un juego completo"""

    app_id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=500)
    release_date = models.CharField(max_length=50, null=True, blank=True)
    required_age = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dlc_count = models.IntegerField(null=True, blank=True)
    detailed_description = models.TextField(null=True, blank=True)
    about_the_game = models.TextField(null=True, blank=True)
    short_description = models.TextField(null=True, blank=True)

    # Campos para listas (almacenados como JSON)
    developers = models.JSONField(null=True, blank=True)
    publishers = models.JSONField(null=True, blank=True)
    genres = models.JSONField(null=True, blank=True)
    categories = models.JSONField(null=True, blank=True)
    platforms = models.JSONField(null=True, blank=True)

    # Campos adicionales
    user_score = models.IntegerField(null=True, blank=True)
    positive_reviews = models.IntegerField(null=True, blank=True)
    negative_reviews = models.IntegerField(null=True, blank=True)
    recommendations = models.IntegerField(null=True, blank=True)
    achievements = models.IntegerField(null=True, blank=True)

    # Metacritic
    metacritic_score = models.IntegerField(null=True, blank=True)
    metacritic_url = models.TextField(null=True, blank=True)

    # Playtime
    average_playtime_forever = models.IntegerField(null=True, blank=True)
    average_playtime_2weeks = models.IntegerField(null=True, blank=True)
    median_playtime_forever = models.IntegerField(null=True, blank=True)
    median_playtime_2weeks = models.IntegerField(null=True, blank=True)

    # Otros campos que puedan existir en el JSON
    estimated_owners = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        abstract = False

    def __str__(self):
        return f"{self.name} ({self.app_id})"
