import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.RunSQL("CREATE SCHEMA IF NOT EXISTS steam;"),
        migrations.CreateModel(
            name="Games",
            fields=[
                ("app_id", models.TextField(primary_key=True, serialize=False)),
                ("name", models.TextField()),
                ("rel_date", models.DateField()),
                ("req_age", models.IntegerField(blank=True, null=True)),
                (
                    "price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                ("dlc_count", models.IntegerField(blank=True, null=True)),
                ("achievements", models.IntegerField(blank=True, null=True)),
                ("estimated_owners", models.TextField(blank=True, null=True)),
            ],
            options={
                "db_table": 'steam"."games',
            },
        ),
        migrations.CreateModel(
            name="Developers",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("developer", models.TextField(blank=True, null=True)),
                (
                    "app",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="games.games",
                    ),
                ),
            ],
            options={
                "db_table": 'steam"."developers',
            },
        ),
        migrations.CreateModel(
            name="Categories",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("category", models.TextField(blank=True, null=True)),
                (
                    "app",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="games.games",
                    ),
                ),
            ],
            options={
                "db_table": 'steam"."categories',
            },
        ),
        migrations.CreateModel(
            name="audio_languages",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("audio_language", models.TextField(blank=True, null=True)),
                (
                    "app",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="games.games",
                    ),
                ),
            ],
            options={
                "db_table": 'steam"."audio_languages',
            },
        ),
        migrations.CreateModel(
            name="about_game",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("detailed_description", models.TextField(blank=True, null=True)),
                ("about_the_game", models.TextField(blank=True, null=True)),
                ("short_description", models.TextField(blank=True, null=True)),
                (
                    "app",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="games.games",
                    ),
                ),
            ],
            options={
                "db_table": 'steam"."about_game',
            },
        ),
        migrations.CreateModel(
            name="Genres",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("genre", models.TextField(blank=True, null=True)),
                (
                    "app",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="games.games",
                    ),
                ),
            ],
            options={
                "db_table": 'steam"."genres',
            },
        ),
        migrations.CreateModel(
            name="Languages",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("language", models.TextField(blank=True, null=True)),
                (
                    "app",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="games.games",
                    ),
                ),
            ],
            options={
                "db_table": 'steam"."languages',
            },
        ),
        migrations.CreateModel(
            name="Metacritic",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("metacritic_score", models.IntegerField(blank=True, null=True)),
                ("metacritic_url", models.TextField(blank=True, null=True)),
                (
                    "app",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="games.games",
                    ),
                ),
            ],
            options={
                "db_table": 'steam"."metacritic',
            },
        ),
        migrations.CreateModel(
            name="Packages",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("package_title", models.TextField(blank=True, null=True)),
                ("package_description", models.TextField(blank=True, null=True)),
                ("sub_text", models.TextField(blank=True, null=True)),
                ("sub_description", models.TextField(blank=True, null=True)),
                (
                    "sub_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "app",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="games.games",
                    ),
                ),
            ],
            options={
                "db_table": 'steam"."packages',
            },
        ),
        migrations.CreateModel(
            name="Platforms",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("windows", models.BooleanField(blank=True, null=True)),
                ("mac", models.BooleanField(blank=True, null=True)),
                ("linux", models.BooleanField(blank=True, null=True)),
                (
                    "app",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="games.games",
                    ),
                ),
            ],
            options={
                "db_table": 'steam"."platforms',
            },
        ),
        migrations.CreateModel(
            name="Playtime",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("avg_playtime_forever", models.IntegerField(blank=True, null=True)),
                ("avg_playtime_2weeks", models.IntegerField(blank=True, null=True)),
                ("med_playtime_forever", models.IntegerField(blank=True, null=True)),
                ("med_playtime_2weeks", models.IntegerField(blank=True, null=True)),
                (
                    "app",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="games.games",
                    ),
                ),
            ],
            options={
                "db_table": 'steam"."playtime',
            },
        ),
        migrations.CreateModel(
            name="Publishers",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("publisher", models.TextField(blank=True, null=True)),
                (
                    "app",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="games.games",
                    ),
                ),
            ],
            options={
                "db_table": 'steam"."publishers',
            },
        ),
        migrations.CreateModel(
            name="Reviews",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("reviews", models.TextField(blank=True, null=True)),
                (
                    "app",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="games.games",
                    ),
                ),
            ],
            options={
                "db_table": 'steam"."reviews',
            },
        ),
        migrations.CreateModel(
            name="scores_and_ranks",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("user_score", models.IntegerField(blank=True, null=True)),
                ("score_rank", models.TextField(blank=True, null=True)),
                ("positive", models.IntegerField(blank=True, null=True)),
                ("negative", models.IntegerField(blank=True, null=True)),
                ("recommendations", models.IntegerField(blank=True, null=True)),
                (
                    "app",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="games.games",
                    ),
                ),
            ],
            options={
                "db_table": 'steam"."scores_and_ranks',
            },
        ),
        migrations.CreateModel(
            name="Urls",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("website", models.TextField(blank=True, null=True)),
                ("support_url", models.TextField(blank=True, null=True)),
                ("support_email", models.TextField(blank=True, null=True)),
                (
                    "app",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="games.games",
                    ),
                ),
            ],
            options={
                "db_table": 'steam"."urls',
            },
        ),
    ]
