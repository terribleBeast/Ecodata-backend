-- =========================================================
-- EcoData mock data
-- Тестовые данные для демонстрации работы системы
-- =========================================================

BEGIN;

-- =========================================================
-- 1. Системные роли
-- =========================================================

INSERT INTO system_roles (name)
VALUES
    ('guest'),
    ('researcher'),
    ('admin')
ON CONFLICT (name) DO NOTHING;

-- =========================================================
-- 2. Административно-территориальные данные
-- =========================================================

INSERT INTO countries (name)
VALUES
    ('Россия'),
    ('Казахстан')
ON CONFLICT (name) DO NOTHING;

INSERT INTO regions (name, country_id)
SELECT 'Новосибирская область', country_id
FROM countries
WHERE name = 'Россия'
ON CONFLICT (country_id, name) DO NOTHING;

INSERT INTO regions (name, country_id)
SELECT 'Алматинская область', country_id
FROM countries
WHERE name = 'Казахстан'
ON CONFLICT (country_id, name) DO NOTHING;

INSERT INTO districts (name, region_id)
SELECT 'Новосибирский район', region_id
FROM regions
WHERE name = 'Новосибирская область'
ON CONFLICT (region_id, name) DO NOTHING;

INSERT INTO districts (name, region_id)
SELECT 'Карасайский район', region_id
FROM regions
WHERE name = 'Алматинская область'
ON CONFLICT (region_id, name) DO NOTHING;

-- Lines 53-58: settlement_types has no UNIQUE on name, so:
INSERT INTO settlement_types (name)
VALUES ('город'), ('посёлок'), ('село')
ON CONFLICT DO NOTHING;  -- ❌ fails — no unique constraint



INSERT INTO settlement_types (name)
VALUES
    ('город'),
    ('посёлок'),
    ('село')
ON CONFLICT DO NOTHING;

INSERT INTO settlements (name, district_id, settlement_type_id)
SELECT 'Новосибирск', d.district_id, st.settlement_type_id
FROM districts d, settlement_types st
WHERE d.name = 'Новосибирский район'
  AND st.name = 'город'
ON CONFLICT (district_id, settlement_type_id, name) DO NOTHING;

INSERT INTO settlements (name, district_id, settlement_type_id)
SELECT 'Каскелен', d.district_id, st.settlement_type_id
FROM districts d, settlement_types st
WHERE d.name = 'Карасайский район'
  AND st.name = 'город'
ON CONFLICT (district_id, settlement_type_id, name) DO NOTHING;

INSERT INTO streets (name)
VALUES
    ('ул. Ленина'),
    ('ул. Советская'),
    ('пр. Науки')
ON CONFLICT (name) DO NOTHING;

INSERT INTO house_numbers (number)
VALUES
    ('10'),
    ('25'),
    ('7А')
ON CONFLICT DO NOTHING;

INSERT INTO street_settlement_association (street_id, settlement_id)
SELECT s.street_id, se.settlement_id
FROM streets s, settlements se
WHERE s.name = 'ул. Ленина'
  AND se.name = 'Новосибирск'
ON CONFLICT DO NOTHING;

INSERT INTO street_settlement_association (street_id, settlement_id)
SELECT s.street_id, se.settlement_id
FROM streets s, settlements se
WHERE s.name = 'пр. Науки'
  AND se.name = 'Новосибирск'
ON CONFLICT DO NOTHING;

INSERT INTO street_settlement_association (street_id, settlement_id)
SELECT s.street_id, se.settlement_id
FROM streets s, settlements se
WHERE s.name = 'ул. Советская'
  AND se.name = 'Каскелен'
ON CONFLICT DO NOTHING;

INSERT INTO addresses (house_number_id, street_id, settlement_id)
SELECT hn.house_number_id, s.street_id, se.settlement_id
FROM house_numbers hn, streets s, settlements se
WHERE hn.number = '10'
  AND s.name = 'ул. Ленина'
  AND se.name = 'Новосибирск'
ON CONFLICT (house_number_id, street_id, settlement_id) DO NOTHING;

INSERT INTO addresses (house_number_id, street_id, settlement_id)
SELECT hn.house_number_id, s.street_id, se.settlement_id
FROM house_numbers hn, streets s, settlements se
WHERE hn.number = '25'
  AND s.name = 'пр. Науки'
  AND se.name = 'Новосибирск'
ON CONFLICT (house_number_id, street_id, settlement_id) DO NOTHING;

-- =========================================================
-- 3. Организации, должности, исследователи
-- =========================================================

INSERT INTO organization_types (name)
VALUES
    ('университет'),
    ('научно-исследовательский институт'),
    ('лаборатория')
ON CONFLICT (name) DO NOTHING;

INSERT INTO organizations (name, organization_type_id, address_id)
SELECT
    'Новосибирский государственный университет',
    ot.organization_type_id,
    a.address_id
FROM organization_types ot
JOIN addresses a ON TRUE
JOIN streets s ON s.street_id = a.street_id
JOIN settlements se ON se.settlement_id = a.settlement_id
WHERE ot.name = 'университет'
  AND s.name = 'ул. Ленина'
  AND se.name = 'Новосибирск'
LIMIT 1;

INSERT INTO organizations (name, organization_type_id, address_id)
SELECT
    'Лаборатория экологического мониторинга',
    ot.organization_type_id,
    a.address_id
FROM organization_types ot
JOIN addresses a ON TRUE
JOIN streets s ON s.street_id = a.street_id
JOIN settlements se ON se.settlement_id = a.settlement_id
WHERE ot.name = 'лаборатория'
  AND s.name = 'пр. Науки'
  AND se.name = 'Новосибирск'
LIMIT 1;

INSERT INTO jobs (name, description)
VALUES
    ('Научный сотрудник', 'Проводит полевые и лабораторные исследования'),
    ('Ботаник', 'Специалист по систематике и морфологии растений'),
    ('Администратор системы', 'Управляет пользователями и справочниками')
ON CONFLICT (name) DO NOTHING;

-- password_hash здесь тестовый, не использовать в production
INSERT INTO researchers (
    email,
    password_hash,
    system_role_id,
    is_active,
    first_name,
    last_name,
    patronymic,
    phone,
    orcid_link,
    job_id,
    organization_id
)
SELECT
    'ivanov@example.com',
    '$2b$12$mock_hash_ivanov',
    sr.system_role_id,
    TRUE,
    'Иван',
    'Иванов',
    'Сергеевич',
    '+7-913-111-22-33',
    '0000-0001-1111-1111',
    j.job_id,
    o.organization_id
FROM system_roles sr, jobs j, organizations o
WHERE sr.name = 'researcher'
  AND j.name = 'Ботаник'
  AND o.name = 'Новосибирский государственный университет'
ON CONFLICT (email) DO NOTHING;

INSERT INTO researchers (
    email,
    password_hash,
    system_role_id,
    is_active,
    first_name,
    last_name,
    patronymic,
    phone,
    orcid_link,
    job_id,
    organization_id
)
SELECT
    'petrova@example.com',
    '$2b$12$mock_hash_petrova',
    sr.system_role_id,
    TRUE,
    'Анна',
    'Петрова',
    'Александровна',
    '+7-913-222-33-44',
    '0000-0002-2222-2222',
    j.job_id,
    o.organization_id
FROM system_roles sr, jobs j, organizations o
WHERE sr.name = 'researcher'
  AND j.name = 'Научный сотрудник'
  AND o.name = 'Лаборатория экологического мониторинга'
ON CONFLICT (email) DO NOTHING;

INSERT INTO researchers (
    email,
    password_hash,
    system_role_id,
    is_active,
    first_name,
    last_name,
    patronymic,
    phone,
    job_id
)
SELECT
    'admin@example.com',
    '$2b$12$mock_hash_admin',
    sr.system_role_id,
    TRUE,
    'Алексей',
    'Смирнов',
    'Игоревич',
    '+7-913-333-44-55',
    j.job_id
FROM system_roles sr, jobs j
WHERE sr.name = 'admin'
  AND j.name = 'Администратор системы'
ON CONFLICT (email) DO NOTHING;

-- =========================================================
-- 4. Локации наблюдений
-- =========================================================

INSERT INTO locations (address_id, latitude, longitude, description)
SELECT
    a.address_id,
    55.030204,
    82.920430,
    'Городская зона наблюдения рядом с университетским корпусом'
FROM addresses a
JOIN streets s ON s.street_id = a.street_id
JOIN settlements se ON se.settlement_id = a.settlement_id
WHERE s.name = 'ул. Ленина'
  AND se.name = 'Новосибирск'
LIMIT 1;

INSERT INTO locations (address_id, latitude, longitude, description)
SELECT
    a.address_id,
    54.980000,
    82.890000,
    'Парковая зона с высокой антропогенной нагрузкой'
FROM addresses a
JOIN streets s ON s.street_id = a.street_id
JOIN settlements se ON se.settlement_id = a.settlement_id
WHERE s.name = 'пр. Науки'
  AND se.name = 'Новосибирск'
LIMIT 1;

-- =========================================================
-- 4.5. Lookup tables referenced by later inserts
-- =========================================================

INSERT INTO side_of_the_world (name)
VALUES ('north'), ('south'), ('east'), ('west')
ON CONFLICT (name) DO NOTHING;

INSERT INTO location_on_plant (name)
VALUES ('upper_crown'), ('middle_crown'), ('lower_crown')
ON CONFLICT (name) DO NOTHING;

INSERT INTO measurement_units (name, symbol)
VALUES
    ('миллиметр', 'mm'),
    ('сантиметр', 'cm'),
    ('градус', '°'),
    ('миллиграмм', 'mg')
ON CONFLICT (symbol) DO NOTHING;

INSERT INTO morphological_features (name, description, default_unit_id)
SELECT 'left_leaf_width', 'Ширина левой половины листа', mu.measurement_unit_id
FROM measurement_units mu WHERE mu.symbol = 'mm'
UNION ALL
SELECT 'right_leaf_width', 'Ширина правой половины листа', mu.measurement_unit_id
FROM measurement_units mu WHERE mu.symbol = 'mm'
ON CONFLICT (name) DO NOTHING;

-- =========================================================
-- 5. Таксономия и описание растений
-- =========================================================

INSERT INTO genera (latin_name, russian_name)
VALUES
    ('Betula', 'Берёза'),
    ('Populus', 'Тополь'),
    ('Acer', 'Клён')
ON CONFLICT (latin_name) DO NOTHING;

INSERT INTO species (genus_id, latin_name, russian_name)
SELECT genus_id, 'Betula pendula', 'Берёза повислая'
FROM genera
WHERE latin_name = 'Betula'
ON CONFLICT (genus_id, latin_name) DO NOTHING;

INSERT INTO species (genus_id, latin_name, russian_name)
SELECT genus_id, 'Populus tremula', 'Осина'
FROM genera
WHERE latin_name = 'Populus'
ON CONFLICT (genus_id, latin_name) DO NOTHING;

INSERT INTO species (genus_id, latin_name, russian_name)
SELECT genus_id, 'Acer platanoides', 'Клён остролистный'
FROM genera
WHERE latin_name = 'Acer'
ON CONFLICT (genus_id, latin_name) DO NOTHING;

INSERT INTO plant_life_forms (name)
VALUES
    ('дерево'),
    ('кустарник'),
    ('травянистое растение')
ON CONFLICT DO NOTHING;

INSERT INTO leaf_blade_types (name)
VALUES
    ('простая листовая пластинка'),
    ('сложная листовая пластинка'),
    ('лопастная листовая пластинка')
ON CONFLICT DO NOTHING;

INSERT INTO plant_descriptions (
    species_id,
    plant_life_form_id,
    leaf_blade_type_id,
    description
)
SELECT
    sp.species_id,
    plf.plant_life_form_id,
    lbt.leaf_blade_type_id,
    'Листья простые, треугольно-яйцевидные, край зубчатый'
FROM species sp, plant_life_forms plf, leaf_blade_types lbt
WHERE sp.latin_name = 'Betula pendula'
  AND plf.name = 'дерево'
  AND lbt.name = 'простая листовая пластинка';

INSERT INTO plant_descriptions (
    species_id,
    plant_life_form_id,
    leaf_blade_type_id,
    description
)
SELECT
    sp.species_id,
    plf.plant_life_form_id,
    lbt.leaf_blade_type_id,
    'Листья округлые, с волнистым краем, длинные черешки'
FROM species sp, plant_life_forms plf, leaf_blade_types lbt
WHERE sp.latin_name = 'Populus tremula'
  AND plf.name = 'дерево'
  AND lbt.name = 'простая листовая пластинка';

-- =========================================================
-- 6. Растения и исследования
-- =========================================================

INSERT INTO plants (location_id, plant_description_id, description)
SELECT
    l.location_id,
    pd.plant_description_id,
    'Экземпляр берёзы рядом с дорогой, высота около 8 метров'
FROM locations l, plant_descriptions pd
JOIN species sp ON sp.species_id = pd.species_id
WHERE sp.latin_name = 'Betula pendula'
LIMIT 1;

INSERT INTO plants (location_id, plant_description_id, description)
SELECT
    l.location_id,
    pd.plant_description_id,
    'Экземпляр осины в парковой зоне'
FROM locations l, plant_descriptions pd
JOIN species sp ON sp.species_id = pd.species_id
WHERE sp.latin_name = 'Populus tremula'
LIMIT 1;

INSERT INTO researches (
    title,
    goal,
    description,
    status,
    start_date,
    end_date,
    created_by_researcher_id
)
SELECT
    'Оценка морфологической асимметрии листьев в городской среде',
    'Выявить связь между условиями произрастания и морфологическими признаками листьев',
    'Исследование включает сбор изображений листьев, измерение морфологических признаков и анализ результатов.',
    'active',
    DATE '2025-04-01',
    DATE '2025-09-30',
    r.researcher_id
FROM researchers r
WHERE r.email = 'ivanov@example.com';

INSERT INTO researches (
    title,
    goal,
    description,
    status,
    start_date,
    created_by_researcher_id
)
SELECT
    'Мониторинг состояния древесных растений',
    'Оценить состояние древесных растений на основе морфологических и биохимических показателей',
    'Пилотное исследование для проверки функциональности информационной системы EcoData.',
    'draft',
    DATE '2025-05-15',
    r.researcher_id
FROM researchers r
WHERE r.email = 'petrova@example.com';

INSERT INTO researcher_research_association (researcher_id, research_id)
SELECT r.researcher_id, res.research_id
FROM researchers r, researches res
WHERE r.email IN ('ivanov@example.com', 'petrova@example.com')
  AND res.title = 'Оценка морфологической асимметрии листьев в городской среде'
ON CONFLICT DO NOTHING;

INSERT INTO research_plant_association (research_id, plant_id)
SELECT res.research_id, p.plant_id
FROM researches res, plants p
WHERE res.title = 'Оценка морфологической асимметрии листьев в городской среде'
ON CONFLICT DO NOTHING;

-- =========================================================
-- 7. Файлы, изображения, листья
-- =========================================================

INSERT INTO files (
    bucket,
    object_key,
    original_filename,
    mime_type,
    size_bytes,
    checksum,
    uploaded_by_researcher_id
)
SELECT
    'ecodata-images',
    'mock/betula_leaf_001.jpg',
    'betula_leaf_001.jpg',
    'image/jpeg',
    245760,
    'mock_checksum_betula_001',
    r.researcher_id
FROM researchers r
WHERE r.email = 'ivanov@example.com'
ON CONFLICT (bucket, object_key) DO NOTHING;

INSERT INTO files (
    bucket,
    object_key,
    original_filename,
    mime_type,
    size_bytes,
    checksum,
    uploaded_by_researcher_id
)
SELECT
    'ecodata-images',
    'mock/populus_leaf_001.jpg',
    'populus_leaf_001.jpg',
    'image/jpeg',
    198400,
    'mock_checksum_populus_001',
    r.researcher_id
FROM researchers r
WHERE r.email = 'petrova@example.com'
ON CONFLICT (bucket, object_key) DO NOTHING;

INSERT INTO images (
    file_id,
    width_px,
    height_px,
    image_type,
    uploaded_by_researcher_id
)
SELECT
    f.file_id,
    1024,
    768,
    'original',
    f.uploaded_by_researcher_id
FROM files f
WHERE f.object_key = 'mock/betula_leaf_001.jpg'
ON CONFLICT (file_id) DO NOTHING;

INSERT INTO images (
    file_id,
    width_px,
    height_px,
    image_type,
    uploaded_by_researcher_id
)
SELECT
    f.file_id,
    1280,
    960,
    'original',
    f.uploaded_by_researcher_id
FROM files f
WHERE f.object_key = 'mock/populus_leaf_001.jpg'
ON CONFLICT (file_id) DO NOTHING;

INSERT INTO leaves (
    plant_id,
    image_id,
    leaf_index,
    side_of_the_world_id,
    location_on_plant_id
)
SELECT
    p.plant_id,
    i.image_id,
    1,
    sw.side_of_the_world_id,
    lop.location_on_plant_id
FROM plants p, images i, side_of_the_world sw, location_on_plant lop
WHERE i.file_id = (
    SELECT file_id FROM files WHERE object_key = 'mock/betula_leaf_001.jpg'
)
  AND sw.name = 'south'
  AND lop.name = 'middle_crown'
LIMIT 1
ON CONFLICT (image_id, leaf_index) DO NOTHING;

INSERT INTO leaves (
    plant_id,
    image_id,
    leaf_index,
    side_of_the_world_id,
    location_on_plant_id
)
SELECT
    p.plant_id,
    i.image_id,
    1,
    sw.side_of_the_world_id,
    lop.location_on_plant_id
FROM plants p, images i, side_of_the_world sw, location_on_plant lop
WHERE i.file_id = (
    SELECT file_id FROM files WHERE object_key = 'mock/populus_leaf_001.jpg'
)
  AND sw.name = 'east'
  AND lop.name = 'upper_crown'
LIMIT 1
ON CONFLICT (image_id, leaf_index) DO NOTHING;

-- =========================================================
-- 8. Морфологические значения
-- =========================================================

INSERT INTO leaf_morphological_feature_values (
    leaf_id,
    morphological_feature_id,
    measurement_unit_id,
    value
)
SELECT
    l.leaf_id,
    mf.morphological_feature_id,
    mu.measurement_unit_id,
    23.4500
FROM leaves l, morphological_features mf, measurement_units mu
WHERE mf.name = 'left_leaf_width'
  AND mu.symbol = 'mm'
LIMIT 1
ON CONFLICT (leaf_id, morphological_feature_id) DO NOTHING;

INSERT INTO leaf_morphological_feature_values (
    leaf_id,
    morphological_feature_id,
    measurement_unit_id,
    value
)
SELECT
    l.leaf_id,
    mf.morphological_feature_id,
    mu.measurement_unit_id,
    24.1200
FROM leaves l, morphological_features mf, measurement_units mu
WHERE mf.name = 'right_leaf_width'
  AND mu.symbol = 'mm'
LIMIT 1
ON CONFLICT (leaf_id, morphological_feature_id) DO NOTHING;

INSERT INTO leaf_morphological_feature_values (
    leaf_id,
    morphological_feature_id,
    measurement_unit_id,
    value
)
SELECT
    l.leaf_id,
    mf.morphological_feature_id,
    mu.measurement_unit_id,
    41.7000
FROM leaves l, morphological_features mf, measurement_units mu
WHERE mf.name = 'left_angle'
  AND mu.symbol = 'deg'
LIMIT 1
ON CONFLICT (leaf_id, morphological_feature_id) DO NOTHING;

-- =========================================================
-- 9. Биохимический анализ
-- =========================================================

INSERT INTO laboratories (name, organization_id, address_id)
SELECT
    'Центральная лаборатория анализа растений',
    o.organization_id,
    o.address_id
FROM organizations o
WHERE o.name = 'Лаборатория экологического мониторинга'
ON CONFLICT DO NOTHING;

INSERT INTO biochemical_analyses (
    plant_id,
    laboratory_id,
    analysis_date,
    comment
)
SELECT
    p.plant_id,
    lab.laboratory_id,
    DATE '2025-06-10',
    'Пробный биохимический анализ листового материала'
FROM plants p, laboratories lab
WHERE lab.name = 'Центральная лаборатория анализа растений'
LIMIT 1;

INSERT INTO biochemical_analysis_values (
    biochemical_analysis_id,
    biochemical_indicator_id,
    measurement_unit_id,
    value
)
SELECT
    ba.biochemical_analysis_id,
    bi.biochemical_indicator_id,
    mu.measurement_unit_id,
    1.2700
FROM biochemical_analyses ba, biochemical_indicators bi, measurement_units mu
WHERE bi.name = 'chlorophyll_a'
  AND mu.symbol = 'mg/g'
LIMIT 1
ON CONFLICT (biochemical_analysis_id, biochemical_indicator_id) DO NOTHING;

INSERT INTO biochemical_analysis_values (
    biochemical_analysis_id,
    biochemical_indicator_id,
    measurement_unit_id,
    value
)
SELECT
    ba.biochemical_analysis_id,
    bi.biochemical_indicator_id,
    mu.measurement_unit_id,
    0.8400
FROM biochemical_analyses ba, biochemical_indicators bi, measurement_units mu
WHERE bi.name = 'chlorophyll_b'
  AND mu.symbol = 'mg/g'
LIMIT 1
ON CONFLICT (biochemical_analysis_id, biochemical_indicator_id) DO NOTHING;

COMMIT;
