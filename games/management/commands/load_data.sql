-- load_data.sql
\set ON_ERROR_STOP on

-- Antes de ejecutar, en CMD: set PGCLIENTENCODING=WIN1252
-- Asegúrate de usar el esquema steam
SET search_path = steam;

\copy games(app_id,name,rel_date,req_age,price,dlc_count,achievements,estimated_owners) FROM 'C:/Users/franb/OneDrive/Documents/GitHub/Proyect-Dinamita/dataset/tables/games.csv' CSV HEADER ;
\copy about_game(app_id,detailed_description,about_the_game,short_description) FROM 'C:/Users/franb/OneDrive/Documents/GitHub/Proyect-Dinamita/dataset/tables/about_game.csv' CSV HEADER ;
\copy reviews(app_id,reviews) FROM 'C:/Users/franb/OneDrive/Documents/GitHub/Proyect-Dinamita/dataset/tables/reviews.csv' CSV HEADER ;
\copy urls(app_id,website,support_url,support_email) FROM 'C:/Users/franb/OneDrive/Documents/GitHub/Proyect-Dinamita/dataset/tables/urls.csv' CSV HEADER ;
\copy platforms(app_id,windows,mac,linux) FROM 'C:/Users/franb/OneDrive/Documents/GitHub/Proyect-Dinamita/dataset/tables/platforms.csv' CSV HEADER ;
\copy metacritic(app_id,metacritic_score,metacritic_url) FROM 'C:/Users/franb/OneDrive/Documents/GitHub/Proyect-Dinamita/dataset/tables/metacritic.csv' CSV HEADER ;
\copy languages(app_id,language) FROM 'C:/Users/franb/OneDrive/Documents/GitHub/Proyect-Dinamita/dataset/tables/languages.csv' CSV HEADER ;
\copy audio_languages(app_id,audio_language) FROM 'C:/Users/franb/OneDrive/Documents/GitHub/Proyect-Dinamita/dataset/tables/audio_languages.csv' CSV HEADER ;
\copy packages(app_id,package_title,package_description,sub_text,sub_description,sub_price) FROM 'C:/Users/franb/OneDrive/Documents/GitHub/Proyect-Dinamita/dataset/tables/packages.csv' CSV HEADER ;
\copy developers(app_id,developer) FROM 'C:/Users/franb/OneDrive/Documents/GitHub/Proyect-Dinamita/dataset/tables/developers.csv' CSV HEADER ;
\copy publishers(app_id,publisher) FROM 'C:/Users/franb/OneDrive/Documents/GitHub/Proyect-Dinamita/dataset/tables/publishers.csv' CSV HEADER ;
\copy categories(app_id,category) FROM 'C:/Users/franb/OneDrive/Documents/GitHub/Proyect-Dinamita/dataset/tables/categories.csv' CSV HEADER ;
\copy genres(app_id,genre) FROM 'C:/Users/franb/OneDrive/Documents/GitHub/Proyect-Dinamita/dataset/tables/genres.csv' CSV HEADER ;
\copy scores_and_ranks(app_id,user_score,score_rank,positive,negative,recommendations) FROM 'C:/Users/franb/OneDrive/Documents/GitHub/Proyect-Dinamita/dataset/tables/scores_and_ranks.csv' CSV HEADER ;
\copy playtime(app_id,avg_playtime_forever,avg_playtime_2weeks,med_playtime_forever,med_playtime_2weeks) FROM 'C:/Users/franb/OneDrive/Documents/GitHub/Proyect-Dinamita/dataset/tables/playtime.csv' CSV HEADER ;
