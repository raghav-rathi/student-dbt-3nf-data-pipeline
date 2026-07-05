-- ============================================================================
-- SNOWFLAKE MEDALLION PIPELINE POPULATION SCRIPT
-- Executes Bronze, Silver 3NF, Snapshots, and Gold Star Schema in Snowflake
-- Database: HEALTHCARE_DB
-- ============================================================================

USE WAREHOUSE COMPUTE_WH;
USE DATABASE HEALTHCARE_DB;

-- ============================================================================
-- 🟤 1. BRONZE LAYER (Staging Views in HEALTHCARE_DB.BRONZE)
-- ============================================================================
USE SCHEMA BRONZE;

CREATE OR REPLACE VIEW STG_PATIENTS AS
SELECT
    TRIM(id) AS patient_id,
    CAST(birthdate AS DATE) AS birth_date,
    CAST(deathdate AS DATE) AS death_date,
    TRIM(ssn) AS ssn,
    TRIM(first) AS first_name,
    TRIM(last) AS last_name,
    TRIM(gender) AS gender,
    TRIM(race) AS race,
    TRIM(ethnicity) AS ethnicity,
    TRIM(address) AS address,
    TRIM(city) AS city,
    TRIM(state) AS state,
    TRIM(zip) AS zip,
    TRIM(insurance_provider) AS insurance_provider,
    CAST(updated_at AS TIMESTAMP) AS updated_at
FROM HEALTHCARE_DB.STAGING.RAW_PATIENTS;

CREATE OR REPLACE VIEW STG_ENCOUNTERS AS
SELECT
    TRIM(id) AS encounter_id,
    CAST("start" AS TIMESTAMP) AS start_time,
    CAST("stop" AS TIMESTAMP) AS stop_time,
    TRIM(patient) AS patient_id,
    TRIM(organization) AS organization_id,
    TRIM(provider) AS provider_id,
    TRIM(payor) AS payor_id,
    TRIM(encounterclass) AS encounter_class,
    CAST(code AS VARCHAR) AS encounter_code,
    TRIM(description) AS encounter_description,
    CAST(base_encounter_cost AS NUMBER(12,2)) AS base_encounter_cost,
    CAST(total_claim_cost AS NUMBER(12,2)) AS total_claim_cost,
    CAST(payer_coverage AS NUMBER(12,2)) AS payer_coverage,
    CAST(reasoncode AS VARCHAR) AS reason_code,
    TRIM(reasondescription) AS reason_description
FROM HEALTHCARE_DB.STAGING.RAW_ENCOUNTERS;

CREATE OR REPLACE VIEW STG_PROVIDERS AS
SELECT
    TRIM(id) AS provider_id,
    TRIM(organization) AS organization_id,
    TRIM(name) AS doctor_name,
    TRIM(gender) AS gender,
    TRIM(speciality) AS specialty,
    TRIM(address) AS address,
    TRIM(city) AS city,
    TRIM(state) AS state,
    TRIM(zip) AS zip
FROM HEALTHCARE_DB.STAGING.RAW_PROVIDERS;

CREATE OR REPLACE VIEW STG_ORGANIZATIONS AS
SELECT
    TRIM(id) AS organization_id,
    TRIM(name) AS hospital_name,
    TRIM(address) AS address,
    TRIM(city) AS city,
    TRIM(state) AS state,
    TRIM(zip) AS zip,
    TRIM(phone) AS phone,
    CAST(revenue AS NUMBER(12,2)) AS revenue
FROM HEALTHCARE_DB.STAGING.RAW_ORGANIZATIONS;

CREATE OR REPLACE VIEW STG_PAYORS AS
SELECT
    TRIM(id) AS payor_id,
    TRIM(name) AS payor_name,
    TRIM(address) AS address,
    TRIM(city) AS city,
    TRIM(state) AS state,
    TRIM(zip) AS zip,
    TRIM(phone) AS phone
FROM HEALTHCARE_DB.STAGING.RAW_PAYORS;

CREATE OR REPLACE VIEW STG_CONDITIONS AS
SELECT
    CAST("start" AS DATE) AS onset_date,
    CAST("stop" AS DATE) AS resolution_date,
    TRIM(patient) AS patient_id,
    TRIM(encounter) AS encounter_id,
    CAST(code AS VARCHAR) AS condition_code,
    TRIM(description) AS condition_description
FROM HEALTHCARE_DB.STAGING.RAW_CONDITIONS;

CREATE OR REPLACE VIEW STG_MEDICATIONS AS
SELECT
    CAST("start" AS TIMESTAMP) AS start_time,
    CAST("stop" AS TIMESTAMP) AS stop_time,
    TRIM(patient) AS patient_id,
    TRIM(encounter) AS encounter_id,
    CAST(code AS VARCHAR) AS medication_code,
    TRIM(description) AS medication_description,
    CAST(base_cost AS NUMBER(12,2)) AS base_cost,
    CAST(payer_coverage AS NUMBER(12,2)) AS payer_coverage,
    CAST(dispenses AS INT) AS dispenses,
    CAST(totalcost AS NUMBER(12,2)) AS total_cost
FROM HEALTHCARE_DB.STAGING.RAW_MEDICATIONS;

CREATE OR REPLACE VIEW STG_PROCEDURES AS
SELECT
    CAST("start" AS TIMESTAMP) AS start_time,
    CAST("stop" AS TIMESTAMP) AS stop_time,
    TRIM(patient) AS patient_id,
    TRIM(encounter) AS encounter_id,
    CAST(code AS VARCHAR) AS procedure_code,
    TRIM(description) AS procedure_description,
    CAST(base_cost AS NUMBER(12,2)) AS base_cost
FROM HEALTHCARE_DB.STAGING.RAW_PROCEDURES;

CREATE OR REPLACE VIEW STG_CLAIMS AS
SELECT
    TRIM(id) AS claim_id,
    TRIM(patient) AS patient_id,
    TRIM(provider) AS provider_id,
    TRIM(status) AS claim_status,
    CAST(outstandingdate AS DATE) AS outstanding_date,
    CAST(servicedate AS DATE) AS service_date
FROM HEALTHCARE_DB.STAGING.RAW_CLAIMS;


-- ============================================================================
-- ⏳ 2. SNAPSHOT LAYER (SCD Type 2 in HEALTHCARE_DB.SNAPSHOTS)
-- ============================================================================
USE SCHEMA SNAPSHOTS;

CREATE OR REPLACE TABLE SNAPSHOT_PATIENTS AS
SELECT
    patient_id,
    first_name,
    last_name,
    gender,
    race,
    ethnicity,
    address,
    city,
    state,
    zip,
    insurance_provider,
    updated_at AS dbt_valid_from,
    CAST(NULL AS TIMESTAMP) AS dbt_valid_to,
    TRUE AS dbt_is_current
FROM HEALTHCARE_DB.BRONZE.STG_PATIENTS;


-- ============================================================================
-- 🔵 3. SILVER LAYER (3NF Relational Tables in HEALTHCARE_DB.SILVER)
-- ============================================================================
USE SCHEMA SILVER;

CREATE OR REPLACE TABLE DIM_PATIENTS AS
SELECT DISTINCT
    patient_id, first_name, last_name, gender, birth_date, death_date, ssn, race, ethnicity, address, city, state, zip, insurance_provider
FROM HEALTHCARE_DB.BRONZE.STG_PATIENTS
WHERE patient_id IS NOT NULL;

CREATE OR REPLACE TABLE DIM_PROVIDERS AS
SELECT DISTINCT
    provider_id, organization_id, doctor_name, gender, specialty, address, city, state, zip
FROM HEALTHCARE_DB.BRONZE.STG_PROVIDERS
WHERE provider_id IS NOT NULL;

CREATE OR REPLACE TABLE DIM_ORGANIZATIONS AS
SELECT DISTINCT
    organization_id, hospital_name, address, city, state, zip, phone, revenue
FROM HEALTHCARE_DB.BRONZE.STG_ORGANIZATIONS
WHERE organization_id IS NOT NULL;

CREATE OR REPLACE TABLE DIM_PAYORS AS
SELECT DISTINCT
    payor_id, payor_name, address, city, state, zip, phone
FROM HEALTHCARE_DB.BRONZE.STG_PAYORS
WHERE payor_id IS NOT NULL;

CREATE OR REPLACE TABLE FCT_ENCOUNTERS AS
SELECT
    encounter_id,
    patient_id,
    provider_id,
    organization_id,
    payor_id,
    encounter_class,
    encounter_code,
    encounter_description,
    start_time AS encounter_start_at,
    stop_time AS encounter_stop_at,
    DATEDIFF('hour', start_time, stop_time) AS length_of_stay_hours,
    base_encounter_cost,
    total_claim_cost,
    payer_coverage,
    ROUND(total_claim_cost - payer_coverage, 2) AS patient_out_of_pocket_cost,
    reason_code,
    reason_description
FROM HEALTHCARE_DB.BRONZE.STG_ENCOUNTERS;

CREATE OR REPLACE TABLE FCT_CLAIMS AS
SELECT claim_id, patient_id, provider_id, claim_status, outstanding_date, service_date
FROM HEALTHCARE_DB.BRONZE.STG_CLAIMS;

CREATE OR REPLACE TABLE FCT_MEDICATIONS AS
SELECT patient_id, encounter_id, medication_code, medication_description, start_time, stop_time, base_cost, payer_coverage, dispenses, total_cost, ROUND(total_cost - payer_coverage, 2) AS patient_out_of_pocket
FROM HEALTHCARE_DB.BRONZE.STG_MEDICATIONS;

CREATE OR REPLACE TABLE FCT_PROCEDURES AS
SELECT patient_id, encounter_id, procedure_code, procedure_description, start_time, stop_time, base_cost
FROM HEALTHCARE_DB.BRONZE.STG_PROCEDURES;

CREATE OR REPLACE TABLE FCT_CONDITIONS AS
SELECT patient_id, encounter_id, condition_code, condition_description, onset_date, resolution_date
FROM HEALTHCARE_DB.BRONZE.STG_CONDITIONS;


-- ============================================================================
-- 🥇 4. GOLD LAYER (Star Schema in HEALTHCARE_DB.GOLD)
-- ============================================================================
USE SCHEMA GOLD;

CREATE OR REPLACE TABLE GOLD_FCT_PATIENT_ENCOUNTERS AS
SELECT
    e.encounter_id,
    e.encounter_start_at,
    e.encounter_stop_at,
    e.encounter_class,
    e.encounter_description,
    e.patient_id,
    e.provider_id,
    e.organization_id,
    e.payor_id,
    p.gender AS patient_gender,
    p.race AS patient_race,
    p.insurance_provider AS insurance_at_visit,
    d.doctor_name,
    d.specialty AS doctor_specialty,
    o.hospital_name,
    py.payor_name,
    e.base_encounter_cost,
    e.total_claim_cost,
    e.payer_coverage,
    e.patient_out_of_pocket_cost,
    e.length_of_stay_hours
FROM HEALTHCARE_DB.SILVER.FCT_ENCOUNTERS e
LEFT JOIN HEALTHCARE_DB.SILVER.DIM_PATIENTS p ON e.patient_id = p.patient_id
LEFT JOIN HEALTHCARE_DB.SILVER.DIM_PROVIDERS d ON e.provider_id = d.provider_id
LEFT JOIN HEALTHCARE_DB.SILVER.DIM_ORGANIZATIONS o ON e.organization_id = o.organization_id
LEFT JOIN HEALTHCARE_DB.SILVER.DIM_PAYORS py ON e.payor_id = py.payor_id;

CREATE OR REPLACE TABLE GOLD_DIM_PATIENTS AS
WITH encounter_stats AS (
    SELECT
        patient_id,
        COUNT(encounter_id) AS total_encounters,
        SUM(total_claim_cost) AS lifetime_claim_cost,
        SUM(patient_out_of_pocket_cost) AS lifetime_out_of_pocket,
        AVG(length_of_stay_hours) AS avg_length_of_stay_hours
    FROM HEALTHCARE_DB.SILVER.FCT_ENCOUNTERS
    GROUP BY patient_id
)
SELECT
    p.patient_id, p.first_name, p.last_name, p.gender, p.birth_date, p.race, p.ethnicity, p.address, p.city, p.state, p.zip, p.insurance_provider,
    COALESCE(s.total_encounters, 0) AS total_encounters,
    COALESCE(ROUND(s.lifetime_claim_cost, 2), 0.00) AS lifetime_claim_cost,
    COALESCE(ROUND(s.lifetime_out_of_pocket, 2), 0.00) AS lifetime_out_of_pocket,
    COALESCE(ROUND(s.avg_length_of_stay_hours, 1), 0.0) AS avg_length_of_stay_hours
FROM HEALTHCARE_DB.SILVER.DIM_PATIENTS p
LEFT JOIN encounter_stats s ON p.patient_id = s.patient_id;

CREATE OR REPLACE TABLE GOLD_DIM_PROVIDERS AS
WITH provider_stats AS (
    SELECT
        provider_id,
        COUNT(DISTINCT patient_id) AS total_patients_seen,
        COUNT(encounter_id) AS total_encounters_handled,
        SUM(total_claim_cost) AS total_revenue_generated
    FROM HEALTHCARE_DB.SILVER.FCT_ENCOUNTERS
    GROUP BY provider_id
)
SELECT
    d.provider_id, d.doctor_name, d.gender, d.specialty, o.hospital_name, o.city AS hospital_city,
    COALESCE(s.total_patients_seen, 0) AS total_patients_seen,
    COALESCE(s.total_encounters_handled, 0) AS total_encounters_handled,
    COALESCE(ROUND(s.total_revenue_generated, 2), 0.00) AS total_revenue_generated
FROM HEALTHCARE_DB.SILVER.DIM_PROVIDERS d
LEFT JOIN HEALTHCARE_DB.SILVER.DIM_ORGANIZATIONS o ON d.organization_id = o.organization_id
LEFT JOIN provider_stats s ON d.provider_id = s.provider_id;

CREATE OR REPLACE TABLE GOLD_OBT_HEALTHCARE_ANALYTICS AS
SELECT
    fe.encounter_id, fe.encounter_start_at, fe.encounter_stop_at, fe.encounter_class, fe.encounter_description, fe.length_of_stay_hours, fe.total_claim_cost, fe.payer_coverage, fe.patient_out_of_pocket_cost,
    dp.patient_id, dp.first_name AS patient_first_name, dp.last_name AS patient_last_name, dp.gender AS patient_gender, dp.race AS patient_race, dp.birth_date AS patient_birth_date, dp.insurance_provider AS patient_insurance,
    dprov.provider_id, dprov.doctor_name, dprov.specialty AS doctor_specialty,
    dorg.organization_id, dorg.hospital_name, dorg.city AS hospital_city, dorg.state AS hospital_state,
    dpay.payor_id, dpay.payor_name,
    c.condition_description, m.medication_description
FROM HEALTHCARE_DB.SILVER.FCT_ENCOUNTERS fe
LEFT JOIN HEALTHCARE_DB.SILVER.DIM_PATIENTS dp ON fe.patient_id = dp.patient_id
LEFT JOIN HEALTHCARE_DB.SILVER.DIM_PROVIDERS dprov ON fe.provider_id = dprov.provider_id
LEFT JOIN HEALTHCARE_DB.SILVER.DIM_ORGANIZATIONS dorg ON fe.organization_id = dorg.organization_id
LEFT JOIN HEALTHCARE_DB.SILVER.DIM_PAYORS dpay ON fe.payor_id = dpay.payor_id
LEFT JOIN HEALTHCARE_DB.SILVER.FCT_CONDITIONS c ON fe.encounter_id = c.encounter_id
LEFT JOIN HEALTHCARE_DB.SILVER.FCT_MEDICATIONS m ON fe.encounter_id = m.encounter_id;

-- Show completed schemas
SHOW TABLES IN DATABASE HEALTHCARE_DB;
