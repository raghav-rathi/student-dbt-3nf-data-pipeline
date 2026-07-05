-- ============================================================================
-- SNOWFLAKE DATABASE & STAGING SETUP DDL
-- Database: HEALTHCARE_DB
-- ============================================================================

CREATE DATABASE IF NOT EXISTS HEALTHCARE_DB;
USE DATABASE HEALTHCARE_DB;

CREATE SCHEMA IF NOT EXISTS STAGING;
CREATE SCHEMA IF NOT EXISTS BRONZE;
CREATE SCHEMA IF NOT EXISTS SILVER;
CREATE SCHEMA IF NOT EXISTS GOLD;
CREATE SCHEMA IF NOT EXISTS SNAPSHOTS;

USE SCHEMA STAGING;

-- 1. Patients Table
CREATE OR REPLACE TABLE RAW_PATIENTS (
    id VARCHAR, birthdate DATE, deathdate DATE, ssn VARCHAR,
    first VARCHAR, last VARCHAR, gender VARCHAR, race VARCHAR,
    ethnicity VARCHAR, address VARCHAR, city VARCHAR, state VARCHAR,
    zip VARCHAR, insurance_provider VARCHAR, updated_at TIMESTAMP
);

-- 2. Encounters Table
CREATE OR REPLACE TABLE RAW_ENCOUNTERS (
    id VARCHAR, "start" TIMESTAMP, "stop" TIMESTAMP, patient VARCHAR,
    organization VARCHAR, provider VARCHAR, payor VARCHAR,
    encounterclass VARCHAR, code VARCHAR, description VARCHAR,
    base_encounter_cost NUMBER(12,2), total_claim_cost NUMBER(12,2),
    payer_coverage NUMBER(12,2), reasoncode VARCHAR, reasondescription VARCHAR
);

-- 3. Providers Table
CREATE OR REPLACE TABLE RAW_PROVIDERS (
    id VARCHAR, organization VARCHAR, name VARCHAR, gender VARCHAR,
    speciality VARCHAR, address VARCHAR, city VARCHAR, state VARCHAR, zip VARCHAR
);

-- 4. Organizations Table
CREATE OR REPLACE TABLE RAW_ORGANIZATIONS (
    id VARCHAR, name VARCHAR, address VARCHAR, city VARCHAR, state VARCHAR,
    zip VARCHAR, phone VARCHAR, revenue NUMBER(12,2)
);

-- 5. Payors Table
CREATE OR REPLACE TABLE RAW_PAYORS (
    id VARCHAR, name VARCHAR, address VARCHAR, city VARCHAR, state VARCHAR,
    zip VARCHAR, phone VARCHAR
);

-- 6. Conditions Table
CREATE OR REPLACE TABLE RAW_CONDITIONS (
    "start" DATE, "stop" DATE, patient VARCHAR, encounter VARCHAR,
    code VARCHAR, description VARCHAR
);

-- 7. Medications Table
CREATE OR REPLACE TABLE RAW_MEDICATIONS (
    "start" TIMESTAMP, "stop" TIMESTAMP, patient VARCHAR, encounter VARCHAR,
    code VARCHAR, description VARCHAR, base_cost NUMBER(12,2),
    payer_coverage NUMBER(12,2), dispenses INT, totalcost NUMBER(12,2)
);

-- 8. Procedures Table
CREATE OR REPLACE TABLE RAW_PROCEDURES (
    "start" TIMESTAMP, "stop" TIMESTAMP, patient VARCHAR, encounter VARCHAR,
    code VARCHAR, description VARCHAR, base_cost NUMBER(12,2)
);

-- 9. Claims Table
CREATE OR REPLACE TABLE RAW_CLAIMS (
    id VARCHAR, patient VARCHAR, provider VARCHAR, status VARCHAR,
    outstandingdate DATE, servicedate DATE
);

-- External S3 Stage
CREATE OR REPLACE STAGE HEALTHCARE_S3_STAGE
    URL='s3://healthcare-pipeline-harsh/raw/'
    CREDENTIALS=(AWS_KEY_ID='<YOUR_AWS_ACCESS_KEY_ID>' AWS_SECRET_KEY='<YOUR_AWS_SECRET_ACCESS_KEY>')
    FILE_FORMAT=(TYPE='CSV' SKIP_HEADER=1 FIELD_OPTIONALLY_ENCLOSED_BY='"');

-- Bulk Copy Statements
COPY INTO RAW_PATIENTS FROM @HEALTHCARE_S3_STAGE/patients.csv;
COPY INTO RAW_ENCOUNTERS FROM @HEALTHCARE_S3_STAGE/encounters.csv;
COPY INTO RAW_PROVIDERS FROM @HEALTHCARE_S3_STAGE/providers.csv;
COPY INTO RAW_ORGANIZATIONS FROM @HEALTHCARE_S3_STAGE/organizations.csv;
COPY INTO RAW_PAYORS FROM @HEALTHCARE_S3_STAGE/payors.csv;
COPY INTO RAW_CONDITIONS FROM @HEALTHCARE_S3_STAGE/conditions.csv;
COPY INTO RAW_MEDICATIONS FROM @HEALTHCARE_S3_STAGE/medications.csv;
COPY INTO RAW_PROCEDURES FROM @HEALTHCARE_S3_STAGE/procedures.csv;
COPY INTO RAW_CLAIMS FROM @HEALTHCARE_S3_STAGE/claims.csv;
