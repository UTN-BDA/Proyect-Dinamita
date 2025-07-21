from django.db import models


class AboutGame(models.Model):
    app = models.ForeignKey("Games", models.DO_NOTHING, blank=True, null=True)
    detailed_description = models.TextField(blank=True, null=True)
    about_the_game = models.TextField(blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "about_game"


class AudioLanguages(models.Model):
    app = models.ForeignKey("Games", models.DO_NOTHING, blank=True, null=True)
    audio_language = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "audio_languages"


class Categories(models.Model):
    app = models.ForeignKey("Games", models.DO_NOTHING, blank=True, null=True)
    category = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "categories"


class Developers(models.Model):
    app = models.ForeignKey("Games", models.DO_NOTHING, blank=True, null=True)
    developer = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "developers"


class Games(models.Model):
    app_id = models.TextField(primary_key=True)
    name = models.TextField()
    rel_date = models.DateField()
    req_age = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    dlc_count = models.IntegerField(blank=True, null=True)
    achievements = models.IntegerField(blank=True, null=True)
    estimated_owners = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "games"


class Genres(models.Model):
    app = models.ForeignKey(Games, models.DO_NOTHING, blank=True, null=True)
    genre = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "genres"


class Languages(models.Model):
    app = models.ForeignKey(Games, models.DO_NOTHING, blank=True, null=True)
    language = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "languages"


class Metacritic(models.Model):
    app = models.ForeignKey(Games, models.DO_NOTHING, blank=True, null=True)
    metacritic_score = models.IntegerField(blank=True, null=True)
    metacritic_url = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "metacritic"


class Packages(models.Model):
    app = models.ForeignKey(Games, models.DO_NOTHING, blank=True, null=True)
    package_title = models.TextField(blank=True, null=True)
    package_description = models.TextField(blank=True, null=True)
    sub_text = models.TextField(blank=True, null=True)
    sub_description = models.TextField(blank=True, null=True)
    sub_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )

    class Meta:
        db_table = "packages"


class Platforms(models.Model):
    app = models.ForeignKey(Games, models.DO_NOTHING, blank=True, null=True)
    windows = models.BooleanField(blank=True, null=True)
    mac = models.BooleanField(blank=True, null=True)
    linux = models.BooleanField(blank=True, null=True)

    class Meta:
        db_table = "platforms"


class Playtime(models.Model):
    app = models.ForeignKey(Games, models.DO_NOTHING, blank=True, null=True)
    avg_playtime_forever = models.IntegerField(blank=True, null=True)
    avg_playtime_2weeks = models.IntegerField(blank=True, null=True)
    med_playtime_forever = models.IntegerField(blank=True, null=True)
    med_playtime_2weeks = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "playtime"


class Publishers(models.Model):
    app = models.ForeignKey(Games, models.DO_NOTHING, blank=True, null=True)
    publisher = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "publishers"


class Reviews(models.Model):
    app = models.ForeignKey(Games, models.DO_NOTHING, blank=True, null=True)
    reviews = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "reviews"


class ScoresAndRanks(models.Model):
    app = models.ForeignKey(Games, models.DO_NOTHING, blank=True, null=True)
    user_score = models.IntegerField(blank=True, null=True)
    score_rank = models.TextField(blank=True, null=True)
    positive = models.IntegerField(blank=True, null=True)
    negative = models.IntegerField(blank=True, null=True)
    recommendations = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "scores_and_ranks"


class Urls(models.Model):
    app = models.ForeignKey(Games, models.DO_NOTHING, blank=True, null=True)
    website = models.TextField(blank=True, null=True)
    support_url = models.TextField(blank=True, null=True)
    support_email = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "urls"
