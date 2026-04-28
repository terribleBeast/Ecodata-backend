DROP DATABASE IF EXISTS ecodata;

CREATE DATABASE ecodata
WITH
    OWNER = postgres
    LOCALE_PROVIDER = icu
    ICU_LOCALE = 'ru-RU'
    ENCODING = 'UTF8'
    LC_COLLATE = 'ru_RU.UTF-8'
    LC_CTYPE = 'ru_RU.UTF-8'
    TEMPLATE = template0;

-- Connect to ecodata database
\c ecodata

DROP TABLE IF EXISTS plants;
CREATE TABLE plants (
    plant_id UUID PRIMARY KEY,
    genus VARCHAR(40),
    species VARCHAR(40)
);

DROP TABLE IF EXISTS neural_models;  -- Consistent name
CREATE TABLE neural_models (  -- Consistent name (plural)
    neural_model_id UUID PRIMARY KEY,
    plant_id UUID REFERENCES plants (plant_id),  -- Schema qualified
    model_name VARCHAR(15)
);
