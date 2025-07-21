## Proyecto Dinamita

> **Recomendación:** para tareas de base de datos (creación, importación, restauración), se sugiere usar **pgAdmin** para mayor facilidad.

Simulación de la base de datos de una distribuidora digital de videojuegos. Incluye miles de registros y metadatos para análisis y desarrollo de aplicaciones de Business Data Analytics (BDA).

---

## Tabla de contenidos

- [Requisitos](#requisitos)
- [Instalación rápida](#instalaci%C3%B3n-r%C3%A1pida)
- [Configuración del entorno](#configuraci%C3%B3n-del-entorno)
- [Migraciones y arranque](#migraciones-y-arranque)
- [Importación de datos](#importaci%C3%B3n-de-datos)
- [Uso de ramas de features](#uso-de-ramas-de-features)
- [Equipo de desarrollo](#equipo-de-desarrollo)
- [Limitaciones conocidas](#limitaciones-conocidas)

---

## Requisitos

- **Git** (>= 2.0)
- **Python** (>= 3.13.5)
- **pip** (incluido en Python)
- **PostgreSQL** (>= 17.5)
- **IDE** (recomendado VS Code)
- **Navegador web**

---

## Instalación rápida

1. **Clonar el repositorio**

   ```bash
   git clone https://github.com/UTN-BDA/Proyect-Dinamita.git
   cd Proyect-Dinamita
   ```

   > **Problemas comunes:**
   >
   > - `git: command not found`: instala Git y verifica tu PATH.
   > - Permiso denegado (publickey): configura tu clave SSH o usa HTTPS.

2. **Crear y activar entorno virtual**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate    # Linux/macOS
   .venv\\Scripts\\activate     # Windows
   ```

   > **Problemas comunes:**
   >
   > - Módulo `venv` no disponible: instala el paquete de venv del sistema (p.ej. `sudo apt install python3-venv`).
   > - `activate` no ejecutable: verifica permisos o usa la ruta completa.

3. **Instalar dependencias**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

   > **Problemas comunes:**
   >
   > - Error de compilación de paquetes: instala herramientas de compilación (`build-essential`, `libpq-dev`).
   > - `requires-python` incompatibles: revisa la versión de Python.

---

## Configuración del entorno

1. **Copiar variables de entorno**

Se puede simplemente crear un archivo `.env` o utilizar los siguientes comandos:

```bash
cp .env_example .env      # Linux/macOS
Copy-Item .\.env_example .\.env   # PowerShell
```

> **Problemas comunes:**
>
> - Archivo `env_example` no encontrado: verifica que estás en el directorio raíz.

2. **Editar `.env`**
   Completa:

   ```dotenv
   SECRET_KEY="<tu_clave_secreta>"
   DB_ENGINE="django.db.backends.postgresql"
   DB_NAME="steamdb"
   DB_USER="tu_usuario"
   DB_PASSWORD="tu_contraseña"
   DB_HOST="localhost"
   DB_PORT="5432"
   ```

   > **Problemas comunes:**
   >
   > - Variables sin comillas: Django puede no leerlas correctamente.

3. **Crear la base de datos con psql**

Si bien se puede hacer con `psql` también se puede hacer con `pgadmin`:

```bash
psql -U <tu_usuario> -c "CREATE DATABASE steamdb;"
```

> **Problemas comunes:**
>
> - `psql: command not found`: agrega el binario de PostgreSQL al PATH.
> - `role "<tu_usuario>" does not exist`: crea el rol o usa `postgres`.
> - Permiso denegado: ejecuta con un superusuario.

---

## Migraciones y arranque

```bash
# Aplicar migraciones
python manage.py migrate

# Iniciar servidor
python manage.py runserver
```

> **Problemas comunes:**
>
> - `ModuleNotFoundError`: activa el entorno virtual.
> - `django.core.exceptions.ImproperlyConfigured`: revisa las variables en `.env`.

Accede a `http://127.0.0.1:8000/` en tu navegador.

---

## Importación de datos

> **Nota:** Los datos (CSVs y backup) no están en este repositorio. Descárgalos desde Kaggle:
> [https://www.kaggle.com/datasets/frangcisneros/games-dataset-for-bda](https://www.kaggle.com/datasets/frangcisneros/games-dataset-for-bda)

Este proyecto ofrece dos métodos de carga, siendo la restauración de backup la opción recomendada:

### Opción 1 (recomendada): Restaurar backup completo

1. Copia el archivo `backup_completo` (sin extensión) en la raíz del proyecto.
2. **Con pgAdmin (recomendado)**:

   - Abre **pgAdmin** y conéctate al servidor.
   - Haz clic derecho en la base `steamdb` → **Restore...**
   - En la ventana de restauración:
     - En **Format**, elige `Custom or Tar` y luego pulsa para seleccionar el archivo.
     - En la ventana de "seleccion de archivo" de Windows seleccionar "Todos los archivos" para ver `backup_completo`
     - Marca la casilla **Disable triggers** (en la parte de opciones) para evitar conflictos.
     - Marcar `Only Data` para que no copie las tablas y esquemas ya que las migraciones lo explican.
     - Pulsar **Restore**.

3. **Con psql** (si prefieres):

   ```bash
   pg_restore --dbname=steamdb --verbose --format=tar backup_completo
   ```

   > **Problemas comunes:**
   >
   > - `pg_restore: command not found`: añade PostgreSQL al PATH.
   > - Error de permisos: usa un rol con suficientes privilegios.

### Opción 2: Importar múltiples CSVs

: Importar múltiples CSVs: Importar múltiples CSVs

1. Coloca todos los archivos CSV en la raíz del proyecto:

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

2. Crea un script `import_all_csv.sql` con los `\copy` en el orden de dependencias:

   ```sql
   \copy games FROM 'games.csv' CSV HEADER;
   -- luego: developers, publishers, categories, genres, languages, audio_languages, platforms
   -- luego: playtime, reviews, scores_and_ranks, urls, metacritic, packages, about_game
   ```

3. Ejecuta con psql:

   ```bash
   psql -d steamdb -U <tu_usuario> -f import_all_csv.sql
   ```

> **Problemas comunes:**
>
> - CSV mal formateado (delimitador o encoding): asegúrate de UTF-8 y `,` como separador.
> - Tablas inexistentes: aplica migraciones antes.

---

## Uso de ramas de features

```bash
git fetch origin
git checkout feature/<nombre_de_feature>
python manage.py runserver
```

---

## Equipo de desarrollo

- Francisco Cisneros
- Dana Guzmán
- Marcelo Sola Bru

---

## Limitaciones conocidas

- ✅ Generación de gráficos.
- ✅ Iniciar/cerrar sesión.
- ✅ Visualización del esquema de BD.
- ✅ Búsqueda de juegos, listar todos.
- ❌ Descargar/Restaurar backup desde la app.

El proyecto, pese a limitaciones, se levanta correctamente siguiendo estos pasos.

---

_Última actualización: 23 de junio de 2025_
