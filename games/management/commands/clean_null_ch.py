# Limpia caracteres nulos de models.py
file_path = r"C:\Users\Francisco\Documents\GitHub\Proyect-Dinamita\games\models.py"

with open(file_path, "rb") as f:
    content = f.read()

# Elimina los bytes nulos
cleaned = content.replace(b"\x00", b"")

with open(file_path, "wb") as f:
    f.write(cleaned)

print("Archivo models.py limpiado de caracteres nulos.")
