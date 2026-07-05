-- ============================================================================
-- SNOWFLAKE INFRASTRUCTURE SETUP & AWS S3 INGESTION SCRIPT
-- Database: HEALTHCARE_DB
-- Schema: STAGING
-- Bucket: s3://healthcare-pipeline-harsh/raw/
-- ============================================================================

-- 1. Create Warehouse, Database, and Schemas
CREATE WAREHOUSE IF NOT EXISTS COMPUTE_WH
  WITH WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;

CREATE DATABASE IF NOT EXISTS HEALTHCARE_DB;

CREATE SCHEMA IF NOT EXISTS HEALTHCARE_DB.STAGING;
CREATE SCHEMA IF NOT EXISTS HEALTHCARE_DB.BRONZE;
CREATE SCHEMA IF NOT EXISTS HEALTHCARE_DB.SILVER;
CREATE SCHEMA IF NOT EXISTS HEALTHCARE_DB.GOLD;
CREATE SCHEMA IF NOT EXISTS HEALTHCARE_DB.SNAPSHOTS;

USE WAREHOUSE COMPUTE_WH;
USE DATABASE HEALTHCARE_DB;
USE SCHEMA STAGING;

-- 2. AWS S3 Storage Integration (Replace AWS_ROLE_ARN with your IAM Role)
CREATE OR REPLACE STORAGE INTEGRATION s3_healthcare_int
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3'
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::272419176264:role/snowflake_s3_role'
  STORAGE_ALLOWED_LOCATIONS = ('s3://healthcare-pipeline-harsh/raw/');

-- 3. File Format for CSV Ingestion
CREATE OR REPLACE FILE FORMAT csv_ff
  TYPE = 'CSV'
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  SKIP_HEADER = 1
  NULL_IF = ('NULL', 'null', '');

-- 4. External Stage pointing to AWS S3
CREATE OR REPLACE STAGE s3_raw_stage
  STORAGE_INTEGRATION = s3_healthcare_int
  URL = 's3://healthcare-pipeline-harsh/raw/'
  FILE_FORMAT = csv_ff;

-- 5. Staging Tables Creation
CREATE OR REPLACE TABLE RAW_ORGANIZATIONS (
    id VARCHAR, name VARCHAR, address VARCHAR, city VARCHAR, state VARCHAR, zip VARCHAR, phone VARCHAR, revenue NUMBER(12,2)
);

CREATE OR REPLACE TABLE RAW_PAYORS (
    id VARCHAR, name VARCHAR, address VARCHAR, city VARCHAR, state VARCHAR, zip VARCHAR, phone VARCHAR
);

CREATE OR REPLACE TABLE RAW_PROVIDERS (
    id VARCHAR, organization VARCHAR, name VARCHAR, gender VARCHAR, speciality VARCHAR, address VARCHAR, city VARCHAR, state VARCHAR, zip VARCHAR
);

CREATE OR REPLACE TABLE RAW_PATIENTS (
    id VARCHAR, birthdate DATE, deathdate DATE, ssn VARCHAR, first VARCHAR, last VARCHAR, gender VARCHAR, race VARCHAR, ethnicity VARCHAR, address VARCHAR, city VARCHAR, state VARCHAR, zip VARCHAR, insurance_provider VARCHAR, updated_at TIMESTAMP
);

CREATE OR REPLACE TABLE RAW_ENCOUNTERS (
    id VARCHAR, start TIMESTAMP, stop TIMESTAMP, patient VARCHAR, organization VARCHAR, provider VARCHAR, payor VARCHAR, encounterclass VARCHAR, code VARCHAR, description VARCHAR, base_encounter_cost NUMBER(12,2), total_claim_cost NUMBER(12,2), payer_coverage NUMBER(12,2), reasoncode VARCHAR, reasondescription VARCHAR
);

CREATE OR REPLACE TABLE RAW_CONDITIONS (
    start DATE, stop DATE, patient VARCHAR, encounter VARCHAR, code VARCHAR, description VARCHAR
);

CREATE OR REPLACE TABLE RAW_MEDICATIONS (
    start TIMESTAMP, stop TIMESTAMP, patient VARCHAR, encounter VARCHAR, code VARCHAR, description VARCHAR, base_cost NUMBER(12,2), payer_coverage NUMBER(12,2), dispenses INT, totalcost NUMBER(12,2)
);

CREATE OR REPLACE TABLE RAW_PROCEDURES (
    start TIMESTAMP, stop TIMESTAMP, patient VARCHAR, encounter VARCHAR, code VARCHAR, description VARCHAR, base_cost NUMBER(12,2)
);

CREATE OR REPLACE TABLE RAW_CLAIMS (
    id VARCHAR, patient VARCHAR, provider VARCHAR, status VARCHAR, outstandingdate DATE, servicedate DATE
);

-- 6. Bulk Copy Commands from S3 Stage into Staging Tables
COPY INTO RAW_ORGANIZATIONS FROM @s3_raw_stage/organizations.csv ON_ERROR = 'CONTINUE';
COPY INTO RAW_PAYORS FROM @s3_raw_stage/payors.csv ON_ERROR = 'CONTINUE';
COPY INTO RAW_PROVIDERS FROM @s3_raw_stage/providers.csv ON_ERROR = 'CONTINUE';
COPY INTO RAW_PATIENTS FROM @s3_raw_stage/patients.csv ON_ERROR = 'CONTINUE';
COPY INTO RAW_ENCOUNTERS FROM @s3_raw_stage/encounters.csv ON_ERROR = 'CONTINUE';
COPY INTO RAW_CONDITIONS FROM @s3_raw_stage/conditions.csv ON_ERROR = 'CONTINUE';
COPY INTO RAW_MEDICATIONS FROM @s3_raw_stage/medications.csv ON_ERROR = 'CONTINUE';
COPY INTO RAW_PROCEDURES FROM @s3_raw_stage/procedures.csv ON_ERROR = 'CONTINUE';
COPY INTO RAW_CLAIMS FROM @s3_raw_stage/claims.csv ON_ERROR = 'CONTINUE';
