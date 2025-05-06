from django.db import models


class Game(models.Model):
    appid = models.TextField(primary_key=True)
    name = models.TextField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    estimated_owners = models.TextField(null=True, blank=True)
    peak_ccu = models.IntegerField(null=True, blank=True)
    required_age = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_dlc_count = models.IntegerField(null=True, blank=True)
    about_the_game = models.TextField(null=True, blank=True)
    supported_languages = models.TextField(null=True, blank=True)
    full_audio_languages = models.TextField(null=True, blank=True)
    reviews = models.TextField(null=True, blank=True)
    header_image = models.TextField(null=True, blank=True)
    website = models.TextField(null=True, blank=True)
    support_url = models.TextField(null=True, blank=True)
    support_email = models.TextField(null=True, blank=True)
    windows = models.BooleanField(default=False)
    mac = models.BooleanField(default=False)
    linux = models.BooleanField(default=False)
    metacritic_score = models.IntegerField(null=True, blank=True)
    metacritic_url = models.TextField(null=True, blank=True)
    user_score = models.FloatField(null=True, blank=True)
    positive = models.IntegerField(null=True, blank=True)
    negative = models.IntegerField(null=True, blank=True)
    score_rank = models.IntegerField(null=True, blank=True)
    achievements = models.IntegerField(null=True, blank=True)
    recommendations = models.IntegerField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    average_playtime_forever = models.IntegerField(null=True, blank=True)
    average_playtime_two_weeks = models.IntegerField(null=True, blank=True)
    median_playtime_forever = models.IntegerField(null=True, blank=True)
    median_playtime_two_weeks = models.IntegerField(null=True, blank=True)
    developers = models.TextField(null=True, blank=True)
    publishers = models.TextField(null=True, blank=True)
    categories = models.TextField(null=True, blank=True)
    genres = models.TextField(null=True, blank=True)
    tags = models.TextField(null=True, blank=True)
    screenshots = models.TextField(null=True, blank=True)
    movies = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "game"
        verbose_name = "Game"
        verbose_name_plural = "Games"

    def __str__(self):
        return f"{self.appid} – {self.name}"
