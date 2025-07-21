#!/usr/bin/env python3
import json
import os
import argparse
from tqdm import tqdm
import pandas as pd

def main(input_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # Cargar JSON objeto con claves app_id
    with open(input_path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    # Convertir a DataFrame orientado por índice
    df = pd.DataFrame.from_dict(raw, orient='index')
    df.index.name = 'app_id'
    df = df.reset_index()

    # Preparar tablas como DataFrames
    games = df[['app_id', 'name', 'release_date', 'required_age', 'price', 'dlc_count', 'achievements', 'estimated_owners']]
    about_game = df[['app_id', 'detailed_description', 'about_the_game', 'short_description']]
    reviews = df[['app_id', 'reviews']]
    urls = df[['app_id', 'website', 'support_url', 'support_email']]
    platforms = df[['app_id', 'windows', 'mac', 'linux']]
    metacritic = df[['app_id', 'metacritic_score', 'metacritic_url']]

    # Explode languages
    languages = df[['app_id', 'supported_languages']].explode('supported_languages').rename(columns={'supported_languages': 'language'})
    audio_languages = df[['app_id', 'full_audio_languages']].explode('full_audio_languages').rename(columns={'full_audio_languages': 'audio_language'})

    # Packages
    pkg_rows = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc='Procesando packages'):
        gid = row['app_id']
        for pkg in row.get('packages', []):
            title = pkg.get('title')
            desc = pkg.get('description')
            for sub in pkg.get('subs', []):
                pkg_rows.append({
                    'app_id': gid,
                    'package_title': title,
                    'package_description': desc,
                    'sub_text': sub.get('text'),
                    'sub_description': sub.get('description'),
                    'sub_price': sub.get('price')
                })
    packages = pd.DataFrame(pkg_rows)

    # Simple lists
    developers = df[['app_id', 'developers']].explode('developers').rename(columns={'developers': 'developer'})
    publishers = df[['app_id', 'publishers']].explode('publishers').rename(columns={'publishers': 'publisher'})
    categories = df[['app_id', 'categories']].explode('categories').rename(columns={'categories': 'category'})
    genres = df[['app_id', 'genres']].explode('genres').rename(columns={'genres': 'genre'})

    # Scores and ranks
    scores = df[['app_id', 'user_score', 'score_rank', 'positive', 'negative', 'recommendations']]

    # Playtime
    playtime = df[['app_id', 'average_playtime_forever', 'average_playtime_2weeks', 'median_playtime_forever', 'median_playtime_2weeks']]

    # Diccionario de DataFrames
    table_dfs = {
        'games': games,
        'about_game': about_game,
        'reviews': reviews,
        'urls': urls,
        'platforms': platforms,
        'metacritic': metacritic,
        'languages': languages,
        'audio_languages': audio_languages,
        'packages': packages,
        'developers': developers,
        'publishers': publishers,
        'categories': categories,
        'genres': genres,
        'scores_and_ranks': scores,
        'playtime': playtime
    }

    # Exportar cada tabla a CSV
    for name, df_table in table_dfs.items():
        out_path = os.path.join(output_dir, f'{name}.csv')
        df_table.to_csv(out_path, index=False)
        print(f'[{name}] Exportados {len(df_table)} filas a {out_path}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Normaliza JSON objeto en tablas CSV separadas')
    parser.add_argument('--input', required=True, help='Ruta al JSON objeto limpio')
    parser.add_argument('--output_dir', required=True, help='Directorio de salida para tablas')
    args = parser.parse_args()
    main(args.input, args.output_dir)
