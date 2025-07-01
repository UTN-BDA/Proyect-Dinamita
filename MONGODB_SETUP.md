# Integración MongoDB - Instrucciones

## Configuración

1. **Instalar MongoDB**: Asegúrate de tener MongoDB instalado y ejecutándose en tu sistema.

2. **Configurar variables de entorno**: Copia `.env.example` a `.env` y configura las variables:

   ```bash
   copy .env.example .env
   ```

3. **Configurar MongoDB** en el archivo `.env`:
   ```
   MONGO_URI=mongodb://localhost:27017/
   MONGO_DB_NAME=steam_games_db
   ```

## Carga de Datos en MongoDB

Para cargar los datos del archivo `games_cleaned.json` en MongoDB, ejecuta:

```bash
python manage.py load_mongodb
```

Si el archivo está en una ubicación diferente:

```bash
python manage.py load_mongodb --file path/to/your/games_cleaned.json
```

## Cambio entre Bases de Datos

1. **Desde la interfaz web**:

   - Ve a la página principal
   - Haz clic en el botón "Cambiar BD" en la parte superior
   - Selecciona el tipo de base de datos que quieres usar

2. **Indicador visual**: En la parte superior de cada página verás un badge que indica qué base de datos está activa:
   - **Badge azul "PostgreSQL"**: Base de datos relacional
   - **Badge verde "MongoDB"**: Base de datos NoSQL

## Características

### Base de Datos Relacional (PostgreSQL)

- Datos normalizados en múltiples tablas
- Relaciones entre entidades
- Consultas SQL complejas
- Integridad referencial

### Base de Datos NoSQL (MongoDB)

- Documentos JSON completos
- Estructura desnormalizada
- Búsquedas flexibles
- Escalabilidad horizontal

## Funcionalidades Disponibles

Todas las funcionalidades de la aplicación funcionan con ambos tipos de base de datos:

- **Búsqueda de juegos**: Por diferentes campos
- **Listado de juegos**: Con filtros por género y letra
- **Gráficos por género**: Estadísticas visuales
- **Paginación**: Navegación eficiente

## Comandos Útiles

```bash
# Verificar estado de MongoDB
python manage.py shell
>>> from games.mongodb_service import MongoDBService
>>> service = MongoDBService()
>>> service.connect()

# Ver cantidad de documentos
>>> service.collection.count_documents({})
```

## Solución de Problemas

1. **Error de conexión a MongoDB**: Verifica que MongoDB esté ejecutándose
2. **No aparecen datos**: Asegúrate de haber ejecutado `load_mongodb`
3. **Error al cambiar BD**: Verifica las configuraciones en `.env`
