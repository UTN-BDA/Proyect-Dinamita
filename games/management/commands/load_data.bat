@echo off
REM --------------------------------------------------
REM load_data.bat  —  Windows CMD script para PostgreSQL
REM Uso: load_data.bat <DB_NAME> <DB_USER> <CSV_DIR>
REM Ejemplo:
REM   load_data.bat steamdb postgres "C:\Users\franb\OneDrive\Documents\GitHub\Proyect-Dinamita\dataset\tables"
REM --------------------------------------------------

if "%~1"=="" (
  echo Error: falta el nombre de la base de datos.
  goto :eof
)
if "%~2"=="" (
  echo Error: falta el usuario de PostgreSQL.
  goto :eof
)
if "%~3"=="" (
  echo Error: falta el directorio de CSVs.
  goto :eof
)

set DB_NAME=%~1
set DB_USER=%~2
set CSV_DIR=%~3
set SCRIPTDIR=%~dp0

REM 1) Crear tablas
psql -U %DB_USER% -d %DB_NAME% -f "%SCRIPTDIR%create_tables.sql"
IF ERRORLEVEL 1 (
  echo Falló la creación de tablas.
  goto :eof
)

REM 2) Importar CSVs uno a uno
psql -U %DB_USER% -d %DB_NAME% -c "SET search_path=steam; \copy games(app_id,name,rel_date,req_age,price,dlc_count,achievements,estimated_owners) FROM '%CSV_DIR%\games.csv' CSV HEADER;"
psql -U %DB_USER% -d %DB_NAME% -c "SET search_path=steam; \copy about_game(app_id,detailed_description,about_the_game,short_description) FROM '%CSV_DIR%\about_game.csv' CSV HEADER;"
psql -U %DB_USER% -d %DB_NAME% -c "SET search_path=steam; \copy reviews(app_id,reviews) FROM '%CSV_DIR%\reviews.csv' CSV HEADER;"
psql -U %DB_USER% -d %DB_NAME% -c "SET search_path=steam; \copy urls(app_id,website,support_url,support_email) FROM '%CSV_DIR%\urls.csv' CSV HEADER;"
psql -U %DB_USER% -d %DB_NAME% -c "SET search_path=steam; \copy platforms(app_id,windows,mac,linux) FROM '%CSV_DIR%\platforms.csv' CSV HEADER;"
psql -U %DB_USER% -d %DB_NAME% -c "SET search_path=steam; \copy metacritic(app_id,metacritic_score,metacritic_url) FROM '%CSV_DIR%\metacritic.csv' CSV HEADER;"
psql -U %DB_USER% -d %DB_NAME% -c "SET search_path=steam; \copy languages(app_id,language) FROM '%CSV_DIR%\languages.csv' CSV HEADER;"
psql -U %DB_USER% -d %DB_NAME% -c "SET search_path=steam; \copy audio_languages(app_id,audio_language) FROM '%CSV_DIR%\audio_languages.csv' CSV HEADER;"
psql -U %DB_USER% -d %DB_NAME% -c "SET search_path=steam; \copy packages(app_id,package_title,package_description,sub_text,sub_description,sub_price) FROM '%CSV_DIR%\packages.csv' CSV HEADER;"
psql -U %DB_USER% -d %DB_NAME% -c "SET search_path=steam; \copy developers(app_id,developer) FROM '%CSV_DIR%\developers.csv' CSV HEADER;"
psql -U %DB_USER% -d %DB_NAME% -c "SET search_path=steam; \copy publishers(app_id,publisher) FROM '%CSV_DIR%\publishers.csv' CSV HEADER;"
psql -U %DB_USER% -d %DB_NAME% -c "SET search_path=steam; \copy categories(app_id,category) FROM '%CSV_DIR%\categories.csv' CSV HEADER;"
psql -U %DB_USER% -d %DB_NAME% -c "SET search_path=steam; \copy genres(app_id,genre) FROM '%CSV_DIR%\genres.csv' CSV HEADER;"
psql -U %DB_USER% -d %DB_NAME% -c "SET search_path=steam; \copy scores_and_ranks(app_id,user_score,score_rank,positive,negative,recommendations) FROM '%CSV_DIR%\scores_and_ranks.csv' CSV HEADER;"
psql -U %DB_USER% -d %DB_NAME% -c "SET search_path=steam; \copy playtime(app_id,avg_playtime_forever,avg_playtime_2weeks,med_playtime_forever,med_playtime_2weeks) FROM '%CSV_DIR%\playtime.csv' CSV HEADER;"

echo.
echo ✅ Carga completada en la base de datos %DB_NAME%.
