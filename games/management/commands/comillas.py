import os
import re

input_dir = r"C:\Users\franb\OneDrive\Documents\GitHub\Proyect-Dinamita\dataset\tables"
pattern = re.compile(r"[^\x00-\x7F]+")  # caracteres NO ASCII

for file in os.listdir(input_dir):
    if file.endswith(".csv"):
        path = os.path.join(input_dir, file)
        print(f"Procesando {file}...")

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        cleaned = pattern.sub("", content)

        with open(path, "w", encoding="utf-8") as f:
            f.write(cleaned)

        print(f"✔ {file} limpio y guardado.")
