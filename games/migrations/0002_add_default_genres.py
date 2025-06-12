from django.db import migrations

def add_default_genres(apps, schema_editor):
    Genre = apps.get_model('games', 'Genre')
    default_genres = [
        "360 Video", "Accounting", "Action", "Adventure", "Animation & Modeling",
        "Audio Production", "Casual", "Design & Illustration", "Documentary",
        "Early Access", "Education", "Episodic", "Free To Play", "Free to Play",
        "Game Development", "Gore", "Indie", "Massively Multiplayer", "Movie",
        "Nudity", "Photo Editing", "RPG", "Racing", "Sexual Content", "Short",
        "Simulation", "Software Training", "Sports", "Strategy", "Tutorial",
        "Utilities", "Video Production", "Violent", "Web Publishing",
    ]
    for genre in default_genres:
        Genre.objects.get_or_create(name=genre)

class Migration(migrations.Migration):

    dependencies = [
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_default_genres),
    ]