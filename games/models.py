from django.db import models

class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
class Game(models.Model):
    app_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    release_date = models.CharField(max_length=50, null=True, blank=True)
    estimated_owners = models.CharField(max_length=50, null=True, blank=True)
    peak_ccu = models.IntegerField(default=0)
    required_age = models.FloatField(default=0)
    price = models.FloatField(default=0)
    about_game = models.TextField(null=True, blank=True)
    developers = models.TextField(null=True, blank=True)
    publishers = models.TextField(null=True, blank=True)
    categories = models.TextField(null=True, blank=True)
    # genres = models.TextField(null=True, blank=True)
    tags = models.TextField(null=True, blank=True)
    screenshots = models.TextField(null=True, blank=True)
    movies = models.TextField(null=True, blank=True)
    genres = models.ManyToManyField(Genre, related_name="games", blank=True)


    def __str__(self):
        return self.name

