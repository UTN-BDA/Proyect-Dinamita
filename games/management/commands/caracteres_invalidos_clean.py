import os

# Ruta base de los CSV
base_path = 'C:/Users/franb/OneDrive/Documents/GitHub/Proyect-Dinamita/dataset/tables/'

# Lista de archivos a limpiar
csv_files = [
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
    'games.csv',  # También por las dudas
]

for filename in csv_files:
    file_path = os.path.join(base_path, filename)
    print(f"Limpieza de caracteres especiales en {filename}...")

    with open(file_path, 'rb') as f:
        content = f.read()

    # Decodifica en UTF-8 ignorando caracteres no válidos
    cleaned_content = content.decode('utf-8', errors='ignore')

    # Guarda el archivo limpio
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)

    print(f"  {filename} limpiado y guardado con codificación UTF-8.")

print("✔️ Todos los archivos han sido limpiados.")
