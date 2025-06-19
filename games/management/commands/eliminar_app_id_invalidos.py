import pandas as pd

# Ruta base donde están los CSV
base_path = 'C:/Users/franb/OneDrive/Documents/GitHub/Proyect-Dinamita/dataset/tables/'

# Cargo los app_id válidos desde games.csv
games = pd.read_csv(base_path + 'games.csv', usecols=['app_id'])
valid_app_ids = set(games['app_id'])

# Lista de archivos a filtrar (excepto games.csv)
files_to_filter = [
    'reviews.csv',
    'about_game.csv',
    'urls.csv',
    'platforms.csv',
    'metacritic.csv',
    'languages.csv',
    'audio_languages.csv',
    'packages.csv',
    'developers.csv',
    'publishers.csv',
    'categories.csv',
    'genres.csv',
    'scores_and_ranks.csv',
    'playtime.csv',
]

for filename in files_to_filter:
    file_path = base_path + filename
    print(f'Procesando {filename}...')

    # Leo solo la columna app_id + resto del archivo
    df = pd.read_csv(file_path)

    # Filtrar filas que tengan app_id en valid_app_ids
    df_filtered = df[df['app_id'].isin(valid_app_ids)]

    # Mostrar cuantos registros se eliminaron
    removed = len(df) - len(df_filtered)
    if removed > 0:
        print(f'  Eliminados {removed} registros con app_id inválidos')

    # Sobrescribir el archivo CSV con los datos filtrados
    df_filtered.to_csv(file_path, index=False)

print('Filtrado completado.')
