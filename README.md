## Proyecto Dinamita

Simulación de la base de datos de una distribuidora digital de videojuegos. Incluye miles de registros y metadatos para análisis y desarrollo de aplicaciones de Business Data Analytics (BDA).

---

## Tabla de contenidos

- [Requisitos](#requisitos)
- [Instalación rápida](#instalaci%C3%B3n-r%C3%A1pida)
- [Configuración del entorno](#configuraci%C3%B3n-del-entorno)
- [Migraciones y arranque](#migraciones-y-arranque)
- [Importación de datos](#importaci%C3%B3n-de-datos)

  - [Opción 1: CSVs individuales](#opci%C3%B3n-1-csvs-individuales)
  - [Opción 2: Backup completo (tar)](#opci%C3%B3n-2-backup-completo-tar)

- [Uso de ramas de features](#uso-de-ramas-de-features)
- [Equipo de desarrollo](#equipo-de-desarrollo)

---

## Requisitos

- **Git**: para clonar el repositorio.
- **Python** (>= 3.13.5). Verificado con Python 3.13.5 Verifica con:

  ```bash
  python --version
  ```

- **pip**: incluido en Python.
- **PostgreSQL** (>= 17.5). Verificado con psql (PostgreSQL) 17.5 Verifica con:

  ```bash
  psql --version
  ```

- **IDE**: recomendado Visual Studio Code.
- **Navegador web**.

---

## Instalación rápida

```bash
# Clonar el repositorio
git clone https://github.com/UTN-BDA/Proyect-Dinamita.git
cd Proyect-Dinamita

# Crear y activar entorno virtual
python3 -m venv .venv
source .venv/bin/activate    # Linux/macOS
.venv\\Scripts\\activate     # Windows

# Actualizar pip e instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Configuración del entorno

1. Copia el archivo de ejemplo de variables de entorno (`.env_example`) al nombre que Django espera (`.env`):

   ```bash
   cp .env_example .env
   ```

   > Si usas Windows PowerShell:
   >
   > ```powershell
   > Copy-Item .\.env_example .\.env
   > ```

2. Abre `.env` y completa las variables:

   ```dotenv
   SECRET_KEY="<tu_clave_secreta>"
   DB_ENGINE="django.db.backends.postgresql"
   DB_NAME="steamdb"
   DB_USER="tu_usuario"
   DB_PASSWORD="tu_contraseña"
   DB_HOST="localhost"
   DB_PORT="5432"
   ```

3. Desde la carpeta base, crea la base de datos en PostgreSQL:

   ```bash
   createdb steamdb
   ```

   > **Alternativa con pgAdmin**:
   >
   > 1. Abre **pgAdmin** y conéctate al servidor local.
   > 2. En el panel de la izquierda, haz clic derecho sobre **Databases** → **Create** → **Database...**
   > 3. Asigna **steamdb** como nombre y guarda.

---

## Migraciones y arranque

```bash
# Aplicar migraciones
django-admin migrate

# Iniciar servidor de desarrollo
python manage.py runserver
```

Accede en el navegador a `http://127.0.0.1:8000/`.

---

## Importación de datos

Nota: Los archivos CSV y el backup no están incluidos en este repositorio. Descárgalos manualmente desde Kaggle:

https://www.kaggle.com/datasets/frangcisneros/games-dataset-for-bda

### Lista de archivos CSV

```
about_game.csv
audio_languages.csv
categories.csv
developers.csv
games.csv
genres.csv
languages.csv
metacritic.csv
packages.csv
platforms.csv
playtime.csv
publishers.csv
reviews.csv
scores_and_ranks.csv
urls.csv
```

#### Opción 1: CSVs individuales

1. Coloca todos los `.csv` en la carpeta raíz del proyecto.
2. Para cada archivo, usa el comando `
copy` de PostgreSQL. Ejemplo para `games.csv`:

   ```sql
   \copy games FROM 'ruta/a/games.csv' WITH (FORMAT csv, HEADER true);
   ```

3. Importa los archivos en el orden de dependencias:

   1. `games.csv`
   2. `developers.csv`, `publishers.csv`, `categories.csv`, `genres.csv`, `languages.csv`, `audio_languages.csv`, `platforms.csv`
   3. `playtime.csv`, `reviews.csv`, `scores_and_ranks.csv`, `urls.csv`, `metacritic.csv`, `packages.csv`, `about_game.csv`

> **Tip**: ejecuta psql en la carpeta del proyecto para rutas relativas:
>
> ```bash
> psql -d steamdb -U tu_usuario -f import_all_csv.sql
> ```
>
> donde `import_all_csv.sql` contiene todos los `\copy` en orden.

**Alternativa con pgAdmin**:

1. Abre **pgAdmin** y conéctate al servidor local.
2. Selecciona la base de datos `steamdb` y abre el **Import/Export Data** desde el menú contextual.
3. Para cada `.csv`, usa el asistente de importación:

   - Selecciona el archivo y mapea columnas.
   - Configura **Formato**: `CSV` y activa **Header**.

4. Importa los archivos en el mismo orden de dependencias.

### Opción 2: Backup completo (TAR)

1. Descarga `backup_completo.tar` en la carpeta raíz.
2. Restaura con:

   ```bash
   pg_restore --dbname=steamdb --verbose --format=tar backup_completo.tar
   ```

**Alternativa con pgAdmin**:

1. Abre **pgAdmin** y conéctate al servidor local.
2. Haz clic derecho sobre la base `steamdb` → **Restore...**
3. En la ventana:

   - **Format**: `Tar`
   - **Filename**: selecciona `backup_completo.tar`

4. Pulsa **Restore** y espera a que termine.

---

## Uso de ramas de features

Para probar desarrollos en curso:

```bash
git fetch origin
git checkout feature/<nombre_de_feature>
python manage.py runserver
```

---

## Equipo de desarrollo

- Francisco Cisneros (@cisneros)
- Dana Guzmán (@dana)
- Marcelo Sola Bru (@marcelo)

---

Limitaciones conocidas

Algunas funcionalidades aún están en desarrollo y pueden no funcionar correctamente. A continuación, el estado actual:

✅ Generación de gráficos.

✅ Iniciar sesión y cerrar sesión.

✅ Visualización del esquema de la base de datos.

❌ Búsqueda de juegos.

❌ Listar todos los juegos.

❌ Descargar backup desde la aplicación.

❌ Restaurar backup desde la aplicación.

Aunque ciertas features no estén disponibles, el proyecto se levanta sin problemas siguiendo los pasos anteriores.

---

Última actualización: 23 de junio de 2025
