import os

input_dir = r"C:\Users\franb\OneDrive\Documents\GitHub\Proyect-Dinamita\dataset\tables"

for file in os.listdir(input_dir):
    if file.endswith(".csv"):
        path = os.path.join(input_dir, file)
        print(f"🧹 Procesando {file}...")

        # 1. Leemos como binario
        with open(path, "rb") as f:
            raw = f.read()

        # 2. Decodificamos ignorando caracteres inválidos
        text = raw.decode("utf-8", errors="ignore")

        # 3. Dividimos en líneas sin romper el CSV (preservamos saltos reales)
        lines = text.splitlines(keepends=True)

        # 4. Eliminamos líneas vacías (ojo: no tocamos comillas ni campos multilinea válidos)
        cleaned_lines = [line for line in lines if line.strip()]

        # 5. Guardamos con codificación limpia
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(cleaned_lines)

        print(f"✔ Limpieza completa: {file}")
