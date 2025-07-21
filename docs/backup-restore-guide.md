# Sistema de Backup y Restore Mejorado

## Descripción General

El sistema de backup y restore ha sido completamente renovado para ofrecer mayor flexibilidad y control sobre las operaciones de respaldo de la base de datos Steam.

## Características Principales

### 🔄 Backup Selectivo

- **Selección de Tablas**: Elige específicamente qué tablas incluir en el backup
- **Opciones de Contenido**:
  - Solo estructura (DDL)
  - Estructura + datos (DDL + DML)
- **Nombres Personalizados**: Asigna nombres específicos a tus archivos de backup
- **Metadatos**: Cada backup incluye información sobre fecha, tablas incluidas y tipo de contenido

### 📥 Restore Inteligente

- **Validación de Archivos**: Solo acepta archivos .sql válidos
- **Opciones de Limpieza**: Posibilidad de truncar tablas antes de restaurar
- **Confirmación de Seguridad**: Múltiples verificaciones antes de ejecutar
- **Detección Automática**: Identifica automáticamente las tablas en el archivo de backup

## Tablas Disponibles

El sistema incluye las siguientes tablas de la aplicación Steam:

- **Games**: Información principal de los juegos
- **AboutGame**: Descripciones detalladas
- **AudioLanguages**: Idiomas de audio disponibles
- **Categories**: Categorías de juegos
- **Developers**: Desarrolladores
- **Genres**: Géneros de juegos
- **Languages**: Idiomas soportados
- **Metacritic**: Puntuaciones de Metacritic
- **Packages**: Información de paquetes
- **Platforms**: Plataformas soportadas
- **Playtime**: Estadísticas de tiempo de juego
- **Publishers**: Editores
- **Reviews**: Reseñas
- **ScoresAndRanks**: Puntuaciones y rankings
- **Urls**: URLs relacionadas

## Proceso de Backup

### 1. Acceso

- Navega a "Gestión de Backups" desde la página principal
- O accede directamente a "Crear Backup"

### 2. Selección de Tablas

- Usa "Seleccionar todas las tablas" para incluir todo
- O marca individualmente las tablas que necesites
- Las tablas seleccionadas se resaltan visualmente

### 3. Configuración

- **Nombre del archivo**: Deja en blanco para generar automáticamente o especifica uno personalizado
- **Incluir datos**: Marca si quieres los datos además de la estructura
- **Fecha y hora**: Se agrega automáticamente al nombre si no especificas uno

### 4. Generación

- El sistema crea el archivo SQL con metadatos
- Se descarga automáticamente al completarse
- Incluye comentarios con información del backup

## Proceso de Restore

### 1. Preparación

- Asegúrate de tener un backup de la base de datos actual
- Verifica que el archivo SQL sea válido y compatible

### 2. Selección de Archivo

- Solo se aceptan archivos con extensión .sql
- El sistema valida el formato antes de procesar

### 3. Opciones de Restore

- **Limpiar tablas**: Trunca las tablas antes de insertar (recomendado para evitar duplicados)
- **Confirmación**: Debes confirmar que entiendes las implicaciones

### 4. Ejecución

- El sistema identifica automáticamente las tablas en el backup
- Si seleccionaste "limpiar tablas", se ejecuta TRUNCATE primero
- Se restauran los datos del archivo SQL

## Seguridad y Validaciones

### Durante el Backup

- ✅ Validación de permisos de usuario (requiere login)
- ✅ Verificación de selección de al menos una tabla
- ✅ Validación de conexión a base de datos
- ✅ Manejo de errores de PostgreSQL

### Durante el Restore

- ✅ Validación de archivo SQL
- ✅ Confirmación múltiple del usuario
- ✅ Detección automática de tablas
- ✅ Rollback en caso de error
- ✅ Limpieza de archivos temporales

## Archivos Generados

### Formato del Nombre de Backup

```
backup_steamdb_YYYYMMDD_HHMMSS.sql
```

### Contenido del Archivo

```sql
-- Backup creado el: 2025-06-30 14:30:15
-- Tablas incluidas: games, genres, developers
-- Incluye datos: Sí
-- Esquema: steam

-- [Contenido SQL generado por pg_dump]
```

## Comandos PostgreSQL Utilizados

### Para Backup

```bash
pg_dump -h HOST -U USER -d DATABASE -f archivo.sql --schema=steam -t steam.tabla1 -t steam.tabla2
```

### Para Restore

```bash
psql -h HOST -U USER -d DATABASE -f archivo.sql -v ON_ERROR_STOP=1
```

## Manejo de Errores

### Errores Comunes y Soluciones

1. **"Error de conexión a PostgreSQL"**

   - Verifica la configuración de la base de datos en settings.py
   - Asegúrate de que PostgreSQL esté ejecutándose

2. **"Archivo de backup vacío"**

   - Verifica que las tablas seleccionadas tengan datos
   - Comprueba los permisos de escritura en el directorio

3. **"Error durante el restore"**

   - Verifica que el archivo SQL sea válido
   - Asegúrate de que las tablas existan en la base de datos

4. **"No se puede truncar tabla"**
   - Puede haber restricciones de foreign key
   - El sistema maneja esto automáticamente con CASCADE

## Recomendaciones de Uso

### Para Backups Regulares

- Selecciona todas las tablas
- Incluye datos completos
- Usa nombres descriptivos con fecha

### Para Backups de Desarrollo

- Selecciona solo las tablas que estás modificando
- Puedes excluir datos para backups más rápidos

### Para Migraciones

- Haz backup completo antes de cualquier cambio importante
- Usa la opción de "limpiar tablas" al restaurar en entornos de prueba

## Limitaciones Actuales

- Solo funciona con PostgreSQL
- Requiere herramientas `pg_dump` y `psql` instaladas
- No incluye backup de usuarios ni permisos
- Los archivos temporales se limpian automáticamente

## Futuras Mejoras Planificadas

- [ ] Backup automático programado
- [ ] Compresión de archivos de backup
- [ ] Historial de backups realizados
- [ ] Backup incremental
- [ ] Soporte para otros motores de base de datos
- [ ] Notificaciones por email
