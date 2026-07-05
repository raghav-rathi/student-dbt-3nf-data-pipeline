# 🏥 End-to-End Healthcare Data Pipeline Proposal: AWS S3 → Snowflake → dbt → Power BI

## Executive Summary

This proposal outlines a production-grade, enterprise-ready **Data Engineering & Business Intelligence Pipeline** built on the industry-standard **Synthea™ Healthcare Relational Dataset** (9 core tables with pre-defined 3NF PK-FK relationships).

The architecture leverages the **AWS S3 + Snowflake + dbt (Medallion Stack)** to showcase advanced data engineering competencies:
- **Cloud Ingestion**: AWS S3 Storage Integration & Snowflake External Stage loading raw CSVs.
- **Bronze Layer (Staging)**: 9 1:1 staging view models with standardized types and naming.
- **Silver Layer (Enterprise 3NF)**: Cleaned relational models, **Incremental loading** for high-volume transactions (`fct_encounters`), **SCD Type 2 Snapshots** (`snapshot_patients`), 7 enterprise transformations, and 25+ dbt data quality & FK relationship tests.
- **Gold Layer (Star Schema / BI OBT)**: Point-in-time analytical joins, conformed dimensions, and a denormalized One Big Table (OBT) exported for Power BI.
- **Power BI Executive Dashboard**: A 4-tab interactive analytics report.

---

## 🏗️ System Architecture & Data Flow

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                             END-TO-END PIPELINE ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  ☁️ AWS S3 BUCKET                                                                           │
│     s3://healthcare-pipeline-data/raw/                                                      │
│     (Synthea CSV files: patients.csv, encounters.csv, providers.csv, claims.csv, etc.)      │
│                                                                                             │
│            │                                                                                │
│            ▼  (Snowflake Storage Integration & External Stage)                              │
│   Snowflake RAW / STAGING Schema (`HEALTHCARE_DB.STAGING`)                                  │
│     • Native `COPY INTO` bulk ingestion from S3 into Snowflake staging tables                │
│                                                                                             │
│ ───────────────────────────────── dbt TRANSFORMATION BOUNDARY ───────────────────────────── │
│                                                                                             │
│            │                                                                                │
│            ▼                                                                                │
│  🟤 BRONZE LAYER (dbt Staging Views: `stg_*`)                                              │
│     • 9 view models (`stg_patients`, `stg_encounters`, `stg_providers`, etc.)              │
│     • Type casting, standardized snake_case naming, timestamp parsing                       │
│                                                                                             │
│            │                                                                                │
│            ▼                                                                                │
│  🔵 SILVER LAYER (3NF Relational Model + Incremental + SCD Type 2 Snapshots)                 │
│     • ⏳ `snapshot_patients` (SCD Type 2 via `dbt snapshot` tracking insurance/address)    │
│     • ⚡ `fct_encounters` (INCREMENTAL model with 3-day lookback window & MERGE strategy)   │
│     • `dim_providers`, `dim_organizations`, `dim_payors`, `fct_claims`, `fct_medications`   │
│     • 25+ dbt automated data quality & FK relationship tests                                │
│                                                                                             │
│            │                                                                                │
│            ▼                                                                                │
│  🥇 GOLD LAYER (Star Schema & BI Export)                                                    │
│     • `gold_fct_patient_encounters` (Point-in-Time Join with SCD Type 2 snapshot)          │
│     • `gold_dim_patients`, `gold_dim_providers`                                             │
│     • Export: `gold_obt_healthcare_analytics.csv`                                           │
│                                                                                             │
│            │                                                                                │
│            ▼                                                                                │
│  📊 POWER BI EXECUTIVE DASHBOARD                                                            │
│     • 4-Tab Interactive Dashboard: Executive Overview, Financials, Operations, Clinical     │
│                                                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ❄️ Phase 1: Snowflake Cloud Infrastructure Setup (DDL)

Executing native Snowflake DDL for secure S3 ingestion:

```sql
-- 1. Create Storage Integration with AWS IAM Role
CREATE OR REPLACE STORAGE INTEGRATION s3_healthcare_int
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3'
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::123456789012:role/snowflake_s3_role'
  STORAGE_ALLOWED_LOCATIONS = ('s3://healthcare-pipeline-data/raw/');

-- 2. File Format for CSV Ingestion
CREATE OR REPLACE FILE FORMAT csv_ff
  TYPE = 'CSV'
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  SKIP_HEADER = 1
  NULL_IF = ('NULL', 'null', '');

-- 3. External Stage Pointing to S3
CREATE OR REPLACE STAGE s3_raw_stage
  STORAGE_INTEGRATION = s3_healthcare_int
  URL = 's3://healthcare-pipeline-data/raw/'
  FILE_FORMAT = csv_ff;

-- 4. Bulk Load Raw CSVs into Snowflake Staging Tables
COPY INTO HEALTHCARE_DB.STAGING.RAW_PATIENTS FROM @s3_raw_stage/patients.csv ON_ERROR = 'CONTINUE';
COPY INTO HEALTHCARE_DB.STAGING.RAW_ENCOUNTERS FROM @s3_raw_stage/encounters.csv ON_ERROR = 'CONTINUE';
COPY INTO HEALTHCARE_DB.STAGING.RAW_PROVIDERS FROM @s3_raw_stage/providers.csv ON_ERROR = 'CONTINUE';
COPY INTO HEALTHCARE_DB.STAGING.RAW_ORGANIZATIONS FROM @s3_raw_stage/organizations.csv ON_ERROR = 'CONTINUE';
COPY INTO HEALTHCARE_DB.STAGING.RAW_PAYORS FROM @s3_raw_stage/payors.csv ON_ERROR = 'CONTINUE';
COPY INTO HEALTHCARE_DB.STAGING.RAW_CONDITIONS FROM @s3_raw_stage/conditions.csv ON_ERROR = 'CONTINUE';
COPY INTO HEALTHCARE_DB.STAGING.RAW_MEDICATIONS FROM @s3_raw_stage/medications.csv ON_ERROR = 'CONTINUE';
COPY INTO HEALTHCARE_DB.STAGING.RAW_PROCEDURES FROM @s3_raw_stage/procedures.csv ON_ERROR = 'CONTINUE';
COPY INTO HEALTHCARE_DB.STAGING.RAW_CLAIMS FROM @s3_raw_stage/claims.csv ON_ERROR = 'CONTINUE';
```

---

## 🛠️ Phase 2: dbt Medallion Architecture

### 🟤 1. Bronze Layer (Staging Views)
- **Files**: `models/bronze/stg_patients.sql`, `stg_encounters.sql`, `stg_providers.sql`, etc.
- **Config**: `materialized='view'`
- **Role**: 1:1 mapping of staging tables with string trimming, date casting, and column renaming to standardized `snake_case`.

---

### 🔵 2. Silver Layer (Cleaned 3NF + Incremental + SCD Type 2)

#### A. Incremental Model (`models/silver/fct_encounters.sql`)
High-volume encounter transactions are loaded incrementally using Snowflake `MERGE`:

```sql
{{ config(
    materialized='incremental',
    unique_key='encounter_id',
    incremental_strategy='merge'
) }}

WITH source AS (
    SELECT * FROM {{ ref('stg_encounters') }}
),

transformed AS (
    SELECT
        encounter_id,
        patient_id,
        provider_id,
        organization_id,
        payor_id,
        CAST(start_time AS TIMESTAMP) AS encounter_start_at,
        CAST(stop_time AS TIMESTAMP) AS encounter_stop_at,
        DATEDIFF('hour', CAST(start_time AS TIMESTAMP), CAST(stop_time AS TIMESTAMP)) AS length_of_stay_hours,
        ROUND(total_claim_cost, 2) AS total_claim_cost,
        ROUND(payer_coverage, 2) AS payer_coverage,
        ROUND(total_claim_cost - payer_coverage, 2) AS patient_out_of_pocket_cost
    FROM source
)

SELECT * FROM transformed

{% if is_incremental() %}
  WHERE encounter_start_at >= (
      SELECT DATEADD('day', -3, MAX(encounter_start_at)) FROM {{ this }}
  )
{% endif %}
```

#### B. SCD Type 2 Snapshot (`snapshots/snapshot_patients.sql`)
Tracks changes to patient address, city, state, and insurance over time:

```sql
{% snapshot snapshot_patients %}

{{
    config(
      target_schema='snapshots',
      unique_key='id',
      strategy='timestamp',
      updated_at='updated_at'
    )
}}

SELECT
    id AS patient_id,
    first_name,
    last_name,
    gender,
    address,
    city,
    state,
    zip,
    insurance_provider,
    updated_at
FROM {{ ref('stg_patients') }}

{% endsnapshot %}
```

#### C. Silver Layer 7 Core Enterprise Transformations
1. **Surrogate Keys**: `md5(patient_id)` for optimized joins.
2. **Duration Metrics**: `DATEDIFF('hour', start, stop)` for stay length.
3. **Out-of-Pocket Split**: `total_claim_cost - payer_coverage`.
4. **Clinical Tiers**: Grouping encounter classes (*Emergency*, *Inpatient*, *Wellness*, *Ambulatory*).
5. **Age Enrichment**: `DATEDIFF('year', birthdate, encounter_start)` for age at admission.
6. **Data Cleansing**: `COALESCE` handling and string whitespace trimming.
7. **Referential Integrity**: 25+ dbt tests enforcing PK uniqueness and FK relationships.

---

### 🥇 3. Gold Layer (Star Schema & BI OBT)

The Gold layer performs a **Point-in-Time Join** between `fct_encounters` and `snapshot_patients` (SCD Type 2) to ensure patient details match their exact insurance/address at the time of the visit:

```sql
-- models/gold/gold_fct_patient_encounters.sql

SELECT
    e.encounter_id,
    e.encounter_start_at,
    
    -- Patient attributes AS THEY WERE at the time of the encounter!
    p.patient_id,
    p.address AS patient_address_at_visit,
    p.insurance_provider AS insurance_at_visit,
    
    -- Doctor & Facility
    d.doctor_name,
    d.speciality AS specialty,
    o.hospital_name,
    
    -- Financial Measures
    e.total_claim_cost,
    e.payer_coverage,
    e.patient_out_of_pocket_cost,
    e.length_of_stay_hours
FROM {{ ref('fct_encounters') }} e
LEFT JOIN {{ ref('snapshot_patients') }} p
    ON e.patient_id = p.patient_id
   AND e.encounter_start_at >= p.dbt_valid_from
   AND (e.encounter_start_at < p.dbt_valid_to OR p.dbt_valid_to IS NULL)
LEFT JOIN {{ ref('dim_providers') }} d ON e.provider_id = d.provider_id
LEFT JOIN {{ ref('dim_organizations') }} o ON e.organization_id = o.organization_id
```

---

## 📊 Phase 3: Power BI Executive Dashboard Specification

The exported Gold OBT (`gold_obt_healthcare_analytics.csv`) powers a **4-Tab Power BI Report**:

### 🎯 Tab 1: Executive KPI Command Center
- **Key Cards**: Total Encounters | Total Billed Claims | Insurance Coverage % | Avg Out-of-Pocket Cost | Avg Stay Duration.
- **Visuals**: Monthly Encounter Trend Line Chart | Visit Class Donut Chart | Top 5 Diagnoses Bar Chart.

### 💰 Tab 2: Financial & Insurance Payer Analysis
- **Visuals**: Payer Performance Matrix (Billed vs Covered vs Copay) | Cost by Visit Type Stacked Bar Chart | Out-of-Pocket by Age Bracket Column Chart.

### 🏥 Tab 3: Hospital & Provider Operational Performance
- **Visuals**: Hospital Revenue & Volume Ranking Bar Chart | Provider Workload Scatter Plot (Patients vs Stay Length vs Revenue) | Specialty Heatmap.

### 🩺 Tab 4: Clinical & Demographic Deep-Dive
- **Visuals**: Demographics Pyramid (Age & Gender) | Disease Prevalence Matrix | Medication Prescription Rates by Condition.

---

## 📂 Repository File Structure

```text
├── DDL/
│   └── snowflake_setup.sql             # Storage Integration, Stage, & COPY INTO commands
├── data/
│   └── synthea_raw/                    # 9 Raw Synthea CSV files
├── dbt_project/
│   ├── dbt_project.yml                 # Project config
│   ├── profiles.yml                    # Snowflake profile
│   ├── models/
│   │   ├── sources/
│   │   │   └── sources.yml             # Snowflake staging tables definition
│   │   ├── bronze/                     # 9 Staging Views (`stg_*`)
│   │   ├── silver/                     # 3NF Cleaned Models (`dim_*`, `fct_*`)
│   │   └── gold/                       # Star Schema & BI OBT (`gold_*`)
│   ├── snapshots/
│   │   └── snapshot_patients.sql       # SCD Type 2 Snapshot
│   └── tests/                          # 25+ PK/FK Relationship Tests
├── power_bi/
│   └── gold_obt_healthcare_analytics.csv
├── SETUP_CREDENTIALS.md                # AWS & Snowflake step-by-step setup guide
├── PROPOSAL_PLAN.md                    # This architecture proposal document
└── README.md                           # Enterprise repository documentation
```

---

## 🧪 Verification Plan

1. **Snowflake DDL Execution**: Run `DDL/snowflake_setup.sql` in Snowflake.
2. **dbt Execution & Test Suite**:
   - `dbt debug` (Verify Snowflake connection)
   - `dbt snapshot` (Build SCD Type 2 patient snapshot)
   - `dbt run` (Build Bronze, Silver 3NF, Gold Star Schema)
   - `dbt test` (Execute 25+ PK uniqueness, non-null, and FK relationship tests)
3. **Power BI Export**: Verify `gold_obt_healthcare_analytics.csv` export.
4. **Git Commit & Push**: Push clean, human-typed code to GitHub.
