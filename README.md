# Proyect-Dinamita

Este proyecto busca simular la base de datos de una distribuidora de videojuegos digital, la base de datos posee miles de items con los cuales trabajar.

# Instrucciones para iniciar el proyecto y luego importar los datos desde el CSV

1. Iniciar un entorno virtual con Python.
2. Instalar los `requirements.txt`.
3. Deben tener el dataset descargado en formato "CSV".
4. Abrir el archivo `import_games.py`.(Proyect-Dinamita\games\management\commands\import_games.py).
5. Reemplazar la ruta (línea 61) por defecto por su ruta donde tenga el CSV.
6. En la consola poner los siguientes comandos.
   - `python manage.py migrate`
   - `python manage.py import_games`

# Miembros del equipo

- Cisneros, Franscisco
- Guzman, Dana
- Sola Bru, Marcelo
