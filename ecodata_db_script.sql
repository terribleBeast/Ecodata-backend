-- EcoData PostgreSQL physical schema
-- Assumptions:
-- 1. Binary files are stored in RustFS/S3. PostgreSQL stores only file metadata.
-- 2. One uploaded image may contain one or more leaves.
-- 3. Leaf analysis outputs such as masks, contours and keypoints are stored as files
--    and connected to leaves through leaf_artifacts.
-- 4. researchers are separated from researchers: researchers = authentication/access;
--    researchers = domain profile.
-- 5. Association tables use composite primary keys where appropriate.

BEGIN;


-- =========================================================
-- ENUM TYPES
-- =========================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'research_status') THEN
        CREATE TYPE research_status AS ENUM ('draft', 'active', 'completed', 'archived');
    END IF;


    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'image_type') THEN
        CREATE TYPE image_type AS ENUM ('original', 'cropped', 'processed', 'visualisation');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'model_type') THEN
        CREATE TYPE model_type AS ENUM (
            'species_classifier',
            'leaf_detector',
            'scaler',
            'morphology_extractor',
            'vein_segmenter',
            'scale_detector'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'leaf_artifact_type') THEN
        CREATE TYPE leaf_artifact_type AS ENUM (
            'mask',
            'corrected_mask',
            'annotation_json',
            'visualisation'
        );
    END IF;
END $$;

-- =========================================================
-- AUTHENTICATION AND researchers
-- =========================================================

CREATE TABLE IF NOT EXISTS system_roles (
    system_role_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE
);

-- =========================================================
-- ORGANISATIONS, JOBS, ADDRESSES, LOCATIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS countries (
    country_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL  UNIQUE
);

CREATE TABLE IF NOT EXISTS regions (
    region_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    country_id UUID NOT NULL REFERENCES countries(country_id) ON DELETE RESTRICT,
    UNIQUE (country_id, name)
);

CREATE TABLE IF NOT EXISTS districts (
    district_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    region_id UUID NOT NULL REFERENCES regions(region_id) ON DELETE RESTRICT,
    UNIQUE (region_id, name)
);

CREATE TABLE IF NOT EXISTS settlement_types (
    settlement_type_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL
);



CREATE TABLE IF NOT EXISTS settlements (
    settlement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    district_id UUID NOT NULL REFERENCES districts(district_id) ON DELETE RESTRICT,
    settlement_type_id UUID NOT NULL REFERENCES settlement_types(settlement_type_id) ON DELETE RESTRICT,
    UNIQUE (district_id, settlement_type_id, name)
);

CREATE TABLE IF NOT EXISTS streets (
    street_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS house_numbers (
    house_number_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    number VARCHAR(50) NOT NULL
);


CREATE TABLE IF NOT EXISTS  street_settlement_association (
    street_id UUID NOT NULL REFERENCES streets(street_id) ON DELETE CASCADE ON UPDATE CASCADE,
    settlement_id UUID NOT NULL REFERENCES settlements(settlement_id) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (street_id, settlement_id)
);

CREATE TABLE IF NOT EXISTS addresses (
    address_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    house_number_id UUID NOT NULL REFERENCES house_numbers(house_number_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    street_id UUID NOT NULL,
    settlement_id UUID NOT NULL,

    FOREIGN KEY (street_id, settlement_id)
        REFERENCES street_settlement_association(street_id, settlement_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    UNIQUE (house_number_id, street_id, settlement_id)
);

CREATE TABLE IF NOT EXISTS organization_types (
    organization_type_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS organizations (
    organization_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    organization_type_id UUID REFERENCES organization_types(organization_type_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    address_id UUID REFERENCES addresses(address_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS researchers (

    -- user fields
    researcher_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    system_role_id UUID NOT NULL REFERENCES system_roles(system_role_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    -- researcher
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    patronymic VARCHAR(100),
    phone VARCHAR(30),
    orcid_link VARCHAR(20) UNIQUE,
    job_id UUID REFERENCES jobs(job_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    organization_id UUID REFERENCES organizations(organization_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS locations (
    location_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    address_id UUID REFERENCES addresses(address_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    latitude NUMERIC(9,6),
    longitude NUMERIC(9,6),
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_locations_latitude CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90),
    CONSTRAINT chk_locations_longitude CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180)
);

-- =========================================================
-- RESEARCHES
-- =========================================================

CREATE TABLE IF NOT EXISTS researches (
    research_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    goal TEXT,
    description TEXT,
    status research_status NOT NULL DEFAULT 'draft',
    start_date DATE,
    end_date DATE,
    created_by_researcher_id UUID REFERENCES researchers(researcher_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_research_dates CHECK (
        start_date IS NULL OR end_date IS NULL OR start_date <= end_date
    )
);

CREATE TABLE IF NOT EXISTS researcher_research_association (
    researcher_id UUID NOT NULL REFERENCES researchers(researcher_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    research_id UUID NOT NULL REFERENCES researches(research_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    joined_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (researcher_id, research_id)
);

-- =========================================================
-- PLANTS AND TAXONOMY
-- =========================================================

CREATE TABLE IF NOT EXISTS genera (
    genus_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    latin_name VARCHAR(150) NOT NULL UNIQUE,
    russian_name VARCHAR(150)
);

CREATE TABLE IF NOT EXISTS species (
    species_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    genus_id UUID NOT NULL REFERENCES genera(genus_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    latin_name VARCHAR(150) NOT NULL,
    russian_name VARCHAR(150),
    UNIQUE (genus_id, latin_name)
);

CREATE TABLE plant_life_forms (
    plant_life_form_id UUID PRIMARY KEY  DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL
);

CREATE TABLE leaf_blade_types (
    leaf_blade_type_id UUID PRIMARY KEY  DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS plant_descriptions (
    plant_description_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    species_id UUID REFERENCES species(species_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    plant_life_form_id UUID NOT NULL REFERENCES plant_life_forms(plant_life_form_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    leaf_blade_type_id UUID NOT NULL REFERENCES leaf_blade_types(leaf_blade_type_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS plants (
    plant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_id UUID REFERENCES locations(location_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    plant_description_id UUID REFERENCES plant_descriptions(plant_description_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS side_of_the_world (
    side_of_the_world_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS location_on_plant (
    location_on_plant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE
);

-- =========================================================
-- FILES, IMAGES, LEAVES, ARTIFACTS AND NEURAL MODELS
-- =========================================================

CREATE TABLE IF NOT EXISTS files (
    file_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bucket VARCHAR(100) NOT NULL,
    object_key TEXT NOT NULL,
    original_filename VARCHAR(255),
    mime_type VARCHAR(100),
    size_bytes BIGINT,
    checksum VARCHAR(128),
    uploaded_by_researcher_id UUID REFERENCES researchers(researcher_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (bucket, object_key),
    CONSTRAINT chk_files_size CHECK (size_bytes IS NULL OR size_bytes >= 0)
);

CREATE TABLE IF NOT EXISTS images (
    image_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID NOT NULL UNIQUE REFERENCES files(file_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    width_px INTEGER,
    height_px INTEGER,
    image_type image_type NOT NULL DEFAULT 'original',
    uploaded_by_researcher_id UUID REFERENCES researchers(researcher_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_images_width CHECK (width_px IS NULL OR width_px > 0),
    CONSTRAINT chk_images_height CHECK (height_px IS NULL OR height_px > 0)
);

CREATE TABLE IF NOT EXISTS leaves (
    leaf_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plant_id UUID NOT NULL REFERENCES plants(plant_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    image_id UUID REFERENCES images(image_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    leaf_index INTEGER,
    side_of_the_world_id UUID REFERENCES side_of_the_world(side_of_the_world_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    location_on_plant_id UUID REFERENCES location_on_plant(location_on_plant_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (image_id, leaf_index),
    CONSTRAINT chk_leaves_leaf_index CHECK (leaf_index IS NULL OR leaf_index > 0)

);
CREATE TABLE IF NOT EXISTS neural_models (
        neural_model_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        file_id UUID NOT NULL UNIQUE REFERENCES files(file_id)
            ON UPDATE CASCADE ON DELETE RESTRICT,
        species_id UUID REFERENCES species(species_id)
            ON UPDATE CASCADE ON DELETE SET NULL,
        model_type model_type NOT NULL,
        input_format TEXT,
        output_format TEXT,
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );



CREATE TABLE IF NOT EXISTS leaf_artifacts (
    leaf_artifact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    leaf_id UUID NOT NULL REFERENCES leaves(leaf_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    file_id UUID NOT NULL REFERENCES files(file_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    artifact_type leaf_artifact_type NOT NULL,
    created_by_model_id UUID REFERENCES neural_models(neural_model_id)
    ON UPDATE CASCADE
    ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (leaf_id, artifact_type, file_id)
);

CREATE TABLE IF NOT EXISTS research_plant_association (
    research_id UUID NOT NULL REFERENCES researches(research_id) ON DELETE CASCADE ON UPDATE CASCADE,
    plant_id UUID NOT NULL REFERENCES plants(plant_id) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (research_id, plant_id)
);




-- =========================================================
-- MORPHOLOGICAL FEATURES
-- =========================================================

CREATE TABLE IF NOT EXISTS measurement_units (
    measurement_unit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    symbol VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS morphological_features (
    morphological_feature_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    default_unit_id UUID REFERENCES measurement_units(measurement_unit_id)
        ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS leaf_morphological_feature_values (
    leaf_id UUID NOT NULL REFERENCES leaves(leaf_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    morphological_feature_id UUID NOT NULL REFERENCES morphological_features(morphological_feature_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    measurement_unit_id UUID REFERENCES measurement_units(measurement_unit_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    value NUMERIC(10,4) NOT NULL,
    measured_by_model_id UUID REFERENCES neural_models(neural_model_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    measured_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (leaf_id, morphological_feature_id),
    CONSTRAINT chk_morph_value CHECK (value >= 0)
);

-- =========================================================
-- BIOCHEMICAL ANALYSIS
-- =========================================================

CREATE TABLE IF NOT EXISTS laboratories (
    laboratory_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    organization_id UUID REFERENCES organizations(organization_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    address_id UUID REFERENCES addresses(address_id)
        ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS biochemical_indicators (
    biochemical_indicator_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    default_unit_id UUID REFERENCES measurement_units(measurement_unit_id)
        ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS biochemical_analyses (
    biochemical_analysis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plant_id UUID NOT NULL REFERENCES plants(plant_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    laboratory_id UUID REFERENCES laboratories(laboratory_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    analysis_date DATE,
    comment TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS biochemical_analysis_values (
    biochemical_analysis_id UUID NOT NULL REFERENCES biochemical_analyses(biochemical_analysis_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    biochemical_indicator_id UUID NOT NULL REFERENCES biochemical_indicators(biochemical_indicator_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    measurement_unit_id UUID REFERENCES measurement_units(measurement_unit_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    value NUMERIC(10,4) NOT NULL,
    PRIMARY KEY (biochemical_analysis_id, biochemical_indicator_id),
    CONSTRAINT chk_biochemical_value CHECK (value >= 0)
);

-- =========================================================
-- INDEXES
-- =========================================================

CREATE INDEX IF NOT EXISTS idx_researchers_email ON researchers(email);
CREATE INDEX IF NOT EXISTS idx_researches_status ON researches(status);
CREATE INDEX IF NOT EXISTS idx_researches_created_by ON researches(created_by_researcher_id);
CREATE INDEX IF NOT EXISTS idx_researcher_research_research_id ON researcher_research_association(research_id);
CREATE INDEX IF NOT EXISTS idx_researcher_research_researcher_id ON researcher_research_association(researcher_id);
CREATE INDEX IF NOT EXISTS idx_plants_location_id ON plants(location_id);
CREATE INDEX IF NOT EXISTS idx_leaves_plant_id ON leaves(plant_id);
CREATE INDEX IF NOT EXISTS idx_leaves_image_id ON leaves(image_id);
CREATE INDEX IF NOT EXISTS idx_files_uploaded_by ON files(uploaded_by_researcher_id);
CREATE INDEX IF NOT EXISTS idx_images_uploaded_by ON images(uploaded_by_researcher_id);
CREATE INDEX IF NOT EXISTS idx_leaf_artifacts_leaf_id ON leaf_artifacts(leaf_id);
CREATE INDEX IF NOT EXISTS idx_leaf_artifacts_file_id ON leaf_artifacts(file_id);
CREATE INDEX IF NOT EXISTS idx_leaf_artifacts_type ON leaf_artifacts(artifact_type);
CREATE INDEX IF NOT EXISTS idx_neural_models_species_id ON neural_models(species_id);
CREATE INDEX IF NOT EXISTS idx_neural_models_type_active ON neural_models(model_type, is_active);
CREATE INDEX IF NOT EXISTS idx_biochemical_analyses_plant_id ON biochemical_analyses(plant_id);
CREATE INDEX IF NOT EXISTS idx_research_plant_research_id
ON research_plant_association(research_id);

CREATE INDEX IF NOT EXISTS idx_research_plant_plant_id
ON research_plant_association(plant_id);

-- =========================================================
-- INITIAL DICTIONARY DATA
-- =========================================================

INSERT INTO system_roles (name)
VALUES
    ('guest'),
    ('researcher'),
    ('admin')
ON CONFLICT (name) DO NOTHING;

INSERT INTO measurement_units (name, symbol)
VALUES
    ('millimetre', 'mm'),
    ('square millimetre', 'mm2'),
    ('degree', 'deg'),
    ('milligram per gram', 'mg/g')
ON CONFLICT (symbol) DO NOTHING;

INSERT INTO morphological_features (name, description, default_unit_id)
SELECT 'left_leaf_width', 'Width of the left half of the leaf', measurement_unit_id
FROM measurement_units WHERE symbol = 'mm'
ON CONFLICT (name) DO NOTHING;

INSERT INTO morphological_features (name, description, default_unit_id)
SELECT 'right_leaf_width', 'Width of the right half of the leaf', measurement_unit_id
FROM measurement_units WHERE symbol = 'mm'
ON CONFLICT (name) DO NOTHING;

INSERT INTO morphological_features (name, description, default_unit_id)
SELECT 'left_second_vein_length', 'Length of the second left secondary vein', measurement_unit_id
FROM measurement_units WHERE symbol = 'mm'
ON CONFLICT (name) DO NOTHING;

INSERT INTO morphological_features (name, description, default_unit_id)
SELECT 'right_second_vein_length', 'Length of the second right secondary vein', measurement_unit_id
FROM measurement_units WHERE symbol = 'mm'
ON CONFLICT (name) DO NOTHING;

INSERT INTO morphological_features (name, description, default_unit_id)
SELECT 'left_angle', 'Angle between the main vein and the second left secondary vein', measurement_unit_id
FROM measurement_units WHERE symbol = 'deg'
ON CONFLICT (name) DO NOTHING;

INSERT INTO morphological_features (name, description, default_unit_id)
SELECT 'right_angle', 'Angle between the main vein and the second right secondary vein', measurement_unit_id
FROM measurement_units WHERE symbol = 'deg'
ON CONFLICT (name) DO NOTHING;

INSERT INTO biochemical_indicators (name, description, default_unit_id)
SELECT 'chlorophyll_a', 'Chlorophyll a content', measurement_unit_id
FROM measurement_units WHERE symbol = 'mg/g'
ON CONFLICT (name) DO NOTHING;

INSERT INTO biochemical_indicators (name, description, default_unit_id)
SELECT 'chlorophyll_b', 'Chlorophyll b content', measurement_unit_id
FROM measurement_units WHERE symbol = 'mg/g'
ON CONFLICT (name) DO NOTHING;

INSERT INTO biochemical_indicators (name, description, default_unit_id)
SELECT 'carotenoids', 'Carotenoid content', measurement_unit_id
FROM measurement_units WHERE symbol = 'mg/g'
ON CONFLICT (name) DO NOTHING;

INSERT INTO side_of_the_world (name)
VALUES ('north'), ('south'), ('east'), ('west')
ON CONFLICT (name) DO NOTHING;

INSERT INTO location_on_plant (name)
VALUES ('lower_crown'), ('middle_crown'), ('upper_crown')
ON CONFLICT (name) DO NOTHING;

COMMIT;
