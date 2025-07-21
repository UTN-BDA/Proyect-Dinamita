import pandas as pd

# Ruta absoluta del archivo de entrada y salida
input_file = r"C:\Users\franb\OneDrive\Documents\GitHub\Proyect-Dinamita\dataset\tables\languages.csv"
output_file = r"C:\Users\franb\OneDrive\Documents\GitHub\Proyect-Dinamita\dataset\tables\languages_pivot.csv"
language_column = "language"

# Cargar el CSV original
df = pd.read_csv(input_file)

# Eliminar filas vacías o con idioma nulo
df = df.dropna(subset=[language_column])

# Crear una columna con valor True para cada fila (presencia del idioma)
df["has_language"] = True

# Pivotar la tabla: filas=app_id, columnas=idioma, valores=True/False
pivot = df.pivot_table(
    index="app_id",
    columns=language_column,
    values="has_language",
    aggfunc="any",
    fill_value=False,
)

# Resetear el índice para tener app_id como columna
pivot = pivot.reset_index()

# Guardar el nuevo CSV
pivot.to_csv(output_file, index=False)

print(f"¡Listo! Archivo guardado como {output_file}")
