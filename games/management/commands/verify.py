import os
from tqdm import tqdm
import chardet

path = r"C:\Users\franb\OneDrive\Documents\GitHub\Proyect-Dinamita\dataset\tables\about_game.csv"

# Detectar encoding
with open(path, "rb") as f:
    raw = f.read(1000000)  # 1MB para detección rápida
    result = chardet.detect(raw)
    original_encoding = result["encoding"]
    print(f"Detectado encoding: {original_encoding}")

# Contar líneas para tqdm
with open(path, "rb") as f:
    total_lines = sum(1 for _ in f)

temp_path = path + ".cleaned"

with open(path, "r", encoding=original_encoding, errors="replace") as infile, \
     open(temp_path, "w", encoding="utf-8") as outfile:

    for line in tqdm(infile, total=total_lines, desc="Limpiando y convirtiendo"):
        # Reemplazar caracteres no UTF-8 con espacio
        clean_line = line.encode("utf-8", errors="replace").decode("utf-8")
        outfile.write(clean_line)

os.replace(temp_path, path)
print("Archivo limpiado y guardado correctamente.")
