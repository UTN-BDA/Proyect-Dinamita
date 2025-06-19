-- create_tables.sql

-- 1. Schema
CREATE SCHEMA IF NOT EXISTS steam;
SET search_path = steam;

-- 2. Tabla principal de juegos
CREATE TABLE games (
    app_id            TEXT     PRIMARY KEY,
    name              TEXT     NOT NULL,
    rel_date          DATE     NOT NULL,
    req_age           INTEGER,
    price             NUMERIC(10,2),
    dlc_count         INTEGER,
    achievements      INTEGER,
    estimated_owners  TEXT
);

-- 3. Descripciones
CREATE TABLE about_game (
    app_id               TEXT    REFERENCES games(app_id),
    detailed_description TEXT,
    about_the_game       TEXT,
    short_description    TEXT
);

-- 4. Reseñas
CREATE TABLE reviews (
    app_id  TEXT REFERENCES games(app_id),
    reviews  TEXT
);

-- 5. URLs
CREATE TABLE urls (
    app_id        TEXT REFERENCES games(app_id),
    website       TEXT,
    support_url   TEXT,
    support_email TEXT
);

-- 6. Plataformas
CREATE TABLE platforms (
    app_id  TEXT    REFERENCES games(app_id),
    windows BOOLEAN,
    mac     BOOLEAN,
    linux   BOOLEAN
);

-- 7. Metacritic
CREATE TABLE metacritic (
    app_id            TEXT    REFERENCES games(app_id),
    metacritic_score  INTEGER,
    metacritic_url    TEXT
);

-- 8. Idiomas
CREATE TABLE languages (
    app_id   TEXT REFERENCES games(app_id),
    language TEXT
);

CREATE TABLE audio_languages (
    app_id         TEXT REFERENCES games(app_id),
    audio_language TEXT
);

-- 9. Paquetes y suscripciones
CREATE TABLE packages (
    app_id              TEXT    REFERENCES games(app_id),
    package_title       TEXT,
    package_description TEXT,
    sub_text            TEXT,
    sub_description     TEXT,
    sub_price           NUMERIC(10,2)
);

-- 10. Desarrolladores y editoras
CREATE TABLE developers (
    app_id    TEXT REFERENCES games(app_id),
    developer TEXT
);

CREATE TABLE publishers (
    app_id   TEXT REFERENCES games(app_id),
    publisher TEXT
);

-- 11. Categorías y géneros
CREATE TABLE categories (
    app_id   TEXT REFERENCES games(app_id),
    category TEXT
);

CREATE TABLE genres (
    app_id TEXT REFERENCES games(app_id),
    genre  TEXT
);

-- 12. Puntuaciones y rankings
CREATE TABLE scores_and_ranks (
    app_id         TEXT REFERENCES games(app_id),
    user_score     INTEGER,
    score_rank     TEXT,
    positive       INTEGER,
    negative       INTEGER,
    recommendations INTEGER
);

-- 13. Tiempos de juego
CREATE TABLE playtime (
    app_id                  TEXT    REFERENCES games(app_id),
    avg_playtime_forever    INTEGER,
    avg_playtime_2weeks     INTEGER,
    med_playtime_forever    INTEGER,
    med_playtime_2weeks     INTEGER
);
