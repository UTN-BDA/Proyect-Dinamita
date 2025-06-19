import os
import chardet

input_dir = r"C:\Users\franb\OneDrive\Documents\GitHub\Proyect-Dinamita\dataset\tables"

for filename in os.listdir(input_dir):
    if filename.endswith(".csv"):
        file_path = os.path.join(input_dir, filename)
        with open(file_path, 'rb') as f:
            raw = f.read()
            detected = chardet.detect(raw)
            encoding = detected['encoding'] or 'utf-8'
        
        # Reescribir el archivo forzando UTF-8
        try:
            text = raw.decode(encoding, errors='replace')  # Reemplaza caracteres ilegales
            with open(file_path, 'w', encoding='utf-8') as f_out:
                f_out.write(text)
            print(f"✅ Convertido: {filename} ({encoding})")
        except Exception as e:
            print(f"❌ Error en {filename}: {e}")
