"""
Script único para exportar datos de PostgreSQL a JSON
Genera un archivo games_export.json con todos los datos de los juegos
"""

import os
import django
import json
import sys
from decimal import Decimal
from datetime import datetime, date

print("Configurando Django...")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "steam_db.settings")
django.setup()

from games.models import (
    Games,
    AboutGame,
    AudioLanguages,
    Categories,
    Developers,
    Genres,
    Languages,
    Metacritic,
    Packages,
    Platforms,
    Playtime,
    Publishers,
    Reviews,
    ScoresAndRanks,
    Urls,
)


class DecimalEncoder(json.JSONEncoder):
    """Encoder personalizado para manejar Decimals y fechas"""

    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        return super().default(o)


def main():
    """Función principal de exportación"""
    output_file = "games_export.json"

    print("=" * 50)
    print("EXPORTANDO DATOS DE POSTGRESQL A JSON")
    print("=" * 50)

    try:
        # Obtener todos los juegos
        games = Games.objects.all()
        total_games = games.count()

        if not total_games:
            print("ERROR: No hay juegos en la base de datos")
            return False

        print(f"Exportando {total_games} juegos...")

        games_data = {}

        for i, game in enumerate(games, 1):
            if i % 500 == 0:
                print(f"Procesando juego {i}/{total_games}...")

            try:
                app_id = str(game.app_id)

                # Datos básicos del juego
                game_data = {
                    "name": game.name,
                    "release_date": game.rel_date,
                    "required_age": game.req_age,
                    "price": game.price,
                    "dlc_count": game.dlc_count,
                    "achievements": game.achievements,
                    "estimated_owners": game.estimated_owners,
                }

                # AboutGame
                try:
                    about = AboutGame.objects.get(app=game)
                    game_data.update(
                        {
                            "detailed_description": about.detailed_description,
                            "about_the_game": about.about_the_game,
                            "short_description": about.short_description,
                        }
                    )
                except AboutGame.DoesNotExist:
                    game_data.update(
                        {
                            "detailed_description": None,
                            "about_the_game": None,
                            "short_description": None,
                        }
                    )

                # Listas relacionadas
                game_data["audio_languages"] = [
                    al.audio_language
                    for al in AudioLanguages.objects.filter(app=game)
                    if al.audio_language
                ]
                game_data["categories"] = [
                    c.category
                    for c in Categories.objects.filter(app=game)
                    if c.category
                ]
                game_data["developers"] = [
                    d.developer
                    for d in Developers.objects.filter(app=game)
                    if d.developer
                ]
                game_data["genres"] = [
                    g.genre for g in Genres.objects.filter(app=game) if g.genre
                ]
                game_data["languages"] = [
                    l.language for l in Languages.objects.filter(app=game) if l.language
                ]
                game_data["publishers"] = [
                    p.publisher
                    for p in Publishers.objects.filter(app=game)
                    if p.publisher
                ]

                # Metacritic
                try:
                    meta = Metacritic.objects.get(app=game)
                    game_data.update(
                        {
                            "metacritic_score": meta.metacritic_score,
                            "metacritic_url": meta.metacritic_url,
                        }
                    )
                except Metacritic.DoesNotExist:
                    game_data.update(
                        {
                            "metacritic_score": None,
                            "metacritic_url": None,
                        }
                    )

                # Packages
                packages = Packages.objects.filter(app=game)
                game_data["packages"] = []
                for package in packages:
                    game_data["packages"].append(
                        {
                            "title": package.package_title,
                            "description": package.package_description,
                            "sub_text": package.sub_text,
                            "sub_description": package.sub_description,
                            "sub_price": package.sub_price,
                        }
                    )

                # Platforms
                try:
                    platform = Platforms.objects.get(app=game)
                    game_data["platforms"] = {
                        "windows": platform.windows,
                        "mac": platform.mac,
                        "linux": platform.linux,
                    }
                except Platforms.DoesNotExist:
                    game_data["platforms"] = {
                        "windows": None,
                        "mac": None,
                        "linux": None,
                    }

                # Playtime
                try:
                    playtime = Playtime.objects.get(app=game)
                    game_data.update(
                        {
                            "average_playtime_forever": playtime.avg_playtime_forever,
                            "average_playtime_2weeks": playtime.avg_playtime_2weeks,
                            "median_playtime_forever": playtime.med_playtime_forever,
                            "median_playtime_2weeks": playtime.med_playtime_2weeks,
                        }
                    )
                except Playtime.DoesNotExist:
                    game_data.update(
                        {
                            "average_playtime_forever": None,
                            "average_playtime_2weeks": None,
                            "median_playtime_forever": None,
                            "median_playtime_2weeks": None,
                        }
                    )

                # Reviews
                try:
                    review = Reviews.objects.get(app=game)
                    game_data["reviews"] = review.reviews
                except Reviews.DoesNotExist:
                    game_data["reviews"] = None

                # ScoresAndRanks
                try:
                    scores = ScoresAndRanks.objects.get(app=game)
                    game_data.update(
                        {
                            "user_score": scores.user_score,
                            "score_rank": scores.score_rank,
                            "positive": scores.positive,
                            "negative": scores.negative,
                            "recommendations": scores.recommendations,
                        }
                    )
                except ScoresAndRanks.DoesNotExist:
                    game_data.update(
                        {
                            "user_score": None,
                            "score_rank": None,
                            "positive": None,
                            "negative": None,
                            "recommendations": None,
                        }
                    )

                # URLs
                try:
                    urls = Urls.objects.get(app=game)
                    game_data["urls"] = {
                        "website": urls.website,
                        "support_url": urls.support_url,
                        "support_email": urls.support_email,
                    }
                except Urls.DoesNotExist:
                    game_data["urls"] = {
                        "website": None,
                        "support_url": None,
                        "support_email": None,
                    }

                games_data[app_id] = game_data

            except Exception as e:
                print(f"ERROR procesando juego {game.app_id}: {e}")
                continue

        # Guardar archivo JSON
        print(f"\nGuardando {len(games_data)} juegos en {output_file}...")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(games_data, f, ensure_ascii=False, indent=2, cls=DecimalEncoder)

        # Estadísticas
        file_size = os.path.getsize(output_file) / (1024 * 1024)
        print(f"✓ Archivo guardado: {output_file}")
        print(f"✓ Juegos exportados: {len(games_data)}")
        print(f"✓ Tamaño del archivo: {file_size:.2f} MB")
        print("✓ Exportación completada exitosamente")

        return True

    except Exception as e:
        print(f"ERROR CRÍTICO: {e}")
        return False


if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n" + "=" * 50)
            print("¡EXPORTACIÓN EXITOSA!")
            print("Archivo 'games_export.json' listo para usar con MongoDB")
            print("=" * 50)
            sys.exit(0)
        else:
            print("\n" + "=" * 50)
            print("ERROR EN LA EXPORTACIÓN")
            print("=" * 50)
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nProceso interrumpido por el usuario.")
        sys.exit(1)
