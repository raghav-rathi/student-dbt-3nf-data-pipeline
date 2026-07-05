# Healthcare Analytics & Medallion Data Pipeline

End-to-End Enterprise Data Engineering Project built with AWS S3, Snowflake Data Warehouse, dbt (data build tool), SCD Type 2 Snapshots, Incremental Models, and an Executive Analytics Dashboard.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Key Architectural Decisions](#key-architectural-decisions)
4. [Data Dictionary & Schema Reference](#data-dictionary--schema-reference)
5. [Analytics & Dashboard Metrics](#analytics--dashboard-metrics)
6. [Setup & Quickstart Guide](#setup--quickstart-guide)

---

## Project Overview

This enterprise data pipeline ingests electronic health record (EHR) data, uploads raw data files into an AWS S3 data lake, loads data into Snowflake Data Warehouse, and transforms it using dbt into a 3NF Medallion Data Architecture (Bronze -> Silver 3NF -> Gold Star Schema).

### Technical Highlights
- AWS S3 Landing Zone: Automated ingestion of 9 core healthcare entities (patients, encounters, providers, organizations, payors, conditions, medications, procedures, claims).
- Snowflake Data Warehouse: Production database setup (`HEALTHCARE_DB`) with bulk COPY INTO staging tables.
- Bronze Layer: 9 staging views with ISO timestamp parsing, header normalization, and string trimming.
- Silver Layer (3NF & Advanced Engineering):
  - Third Normal Form (3NF) relational database design reducing redundancy and data anomalies.
  - Incremental Materialization: High-volume `fct_encounters` table uses `is_incremental()` with a 3-day lookback window & Snowflake MERGE.
  - Slowly Changing Dimension (SCD Type 2): Historical tracking of patient demographic and insurance updates in `snapshots/snapshot_patients.sql` (`dbt_valid_from`, `dbt_valid_to`, `dbt_is_current`).
- Gold Layer (Star Schema & OBT):
  - Dimensional models (`gold_dim_patients`, `gold_dim_providers`) and Fact model (`gold_fct_patient_encounters`).
  - One Big Table (OBT) wide table (`gold_obt_healthcare_analytics`) optimized for low-latency BI queries.
- Data Quality Test Suite: 24 automated dbt tests validating primary key uniqueness, non-null constraints, and foreign key referential integrity (100% PASS rate).
- Executive Analytics Dashboard: Interactive HTML5/CSS3/Chart.js dashboard with dynamic filters for facility, payer, and visit class.

---

## Architecture

```text
  [ Raw Healthcare CSV Files ] (9 Entities)
             │
             ▼
  [ Python Boto3 Uploader ] ──► [ AWS S3 Bucket: s3://healthcare-pipeline-harsh/raw/ ]
                                          │
                                          ▼ (Snowflake COPY INTO)
                            [ Snowflake DW: HEALTHCARE_DB ]
                                          │
 ┌────────────────────────────────────────┴──────────────────────────────────────────────┐
 │                              dbt MEDALLION TRANSFORMATIONS                               │
 ├──────────────────────────────────────────────────────────────────────────────────────────┤
 │                                                                                          │
 │  BRONZE SCHEMA (Views)                                                                   │
 │     stg_patients, stg_encounters, stg_providers, stg_organizations, stg_payors,          │
 │     stg_conditions, stg_medications, stg_procedures, stg_claims                         │
 │                                │                                                         │
 │                                ▼                                                         │
 │  SNAPSHOTS SCHEMA (SCD Type 2)                                                           │
 │     snapshot_patients (dbt_valid_from, dbt_valid_to, dbt_is_current)                     │
 │                                │                                                         │
 │                                ▼                                                         │
 │  SILVER SCHEMA (3NF Relational Tables)                                                   │
 │     dim_patients, dim_providers, dim_organizations, dim_payors                            │
 │     fct_encounters (Incremental), fct_claims, fct_medications, fct_procedures,           │
 │     fct_conditions                                                                       │
 │                                │                                                         │
 │                                ▼                                                         │
 │  GOLD SCHEMA (Star Schema & OBT)                                                         │
 │     gold_fct_patient_encounters, gold_dim_patients, gold_dim_providers                   │
 │     gold_obt_healthcare_analytics (Wide Denormalized Analytics Table)                    │
 │                                                                                          │
 └────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                          │
                                          ▼
                   [ Executive Analytics Dashboard (dashboard.html) ]
                    [ Power BI Report Dataset (obt_analytics.csv) ]
```

---

## Key Architectural Decisions

### 1. AWS S3 Data Lake Storage Layer
- Decouples raw ingestion from downstream compute.
- Preserves raw CSV files for auditability, reprocessing, and historical backfills.

### 2. Snowflake Cloud Data Warehouse
- Independent scaling of storage and compute warehouses (`COMPUTE_WH`).
- Micro-partitioning for fast query execution on analytical queries.
- RSA Key-Pair Authentication (`snowflake_key.p8`) for secure headless execution without password prompts.

### 3. Medallion Architecture (Bronze -> Silver 3NF -> Gold Star Schema)
- Bronze (Staging Views): Type casting, ISO date parsing, header normalization (`snake_case`), and string trimming (`TRIM()`).
- Silver (3NF Relational Core): Third Normal Form (3NF) design separating core entities (`patients`, `providers`, `organizations`, `payors`) from transaction facts.
- Gold (Star Schema & OBT): Pre-aggregates dimensions and metrics into a denormalized One Big Table (OBT) dataset (`gold_obt_healthcare_analytics`) optimized for low-latency BI queries.

### 4. Incremental Materialization (`fct_encounters`)
- Implemented `materialized='incremental'` with a 3-day lookback window:
  ```sql
  {% if is_incremental() %}
    WHERE encounter_start_at >= (
        SELECT COALESCE(MAX(encounter_start_at), CAST('1970-01-01' AS TIMESTAMP)) FROM {{ this }}
    ) - INTERVAL '3 days'
  {% endif %}
  ```
- Uses Snowflake MERGE to insert new records and update existing claims while avoiding full-table scans.

### 5. Slowly Changing Dimensions (SCD Type 2)
- Implemented in `snapshots/snapshot_patients.sql` using `dbt snapshot` (`strategy='timestamp'`, `updated_at='updated_at'`).
- Appends new records when patient address or insurance provider updates occur, populating `dbt_valid_from`, `dbt_valid_to`, and `dbt_is_current`.

---

## Data Dictionary & Schema Reference

### Bronze Layer (`HEALTHCARE_DB.BRONZE`)

| Table / View | Column Name | Data Type | Key Type | Description / Transformation Logic |
| :--- | :--- | :--- | :--- | :--- |
| **`stg_patients`** | `patient_id` | VARCHAR | PK | Cleaned UUID string (`TRIM(id)`). |
| | `first_name` / `last_name` | VARCHAR | - | Trimmed patient full names. |
| | `gender` / `race` / `ethnicity` | VARCHAR | - | Demographic attributes. |
| | `birth_date` / `death_date` | DATE | - | Parsed ISO date fields (`CAST(birthdate AS DATE)`). |
| | `address`, `city`, `state`, `zip` | VARCHAR | - | Geographic location columns. |
| | `insurance_provider` | VARCHAR | - | Primary health insurance carrier. |
| | `updated_at` | TIMESTAMP | - | Timestamp used for SCD Type 2 tracking. |
| **`stg_encounters`** | `encounter_id` | VARCHAR | PK | Unique visit identifier. |
| | `start_time` / `stop_time` | TIMESTAMP | - | Encounter admission & discharge timestamps (`CAST("start" AS TIMESTAMP)`). |
| | `patient_id` | VARCHAR | FK | References `stg_patients.patient_id`. |
| | `organization_id` | VARCHAR | FK | References `stg_organizations.organization_id`. |
| | `provider_id` | VARCHAR | FK | References `stg_providers.provider_id`. |
| | `payor_id` | VARCHAR | FK | References `stg_payors.payor_id`. |
| | `encounter_class` | VARCHAR | - | Visit classification (*Emergency*, *Inpatient*, *Wellness*, *Ambulatory*). |
| | `base_encounter_cost` | NUMBER(12,2) | - | Base hospital facility fee. |
| | `total_claim_cost` | NUMBER(12,2) | - | Gross billed medical claim cost. |
| | `payer_coverage` | NUMBER(12,2) | - | Amount reimbursed by insurance. |
| **`stg_providers`** | `provider_id` | VARCHAR | PK | Doctor unique identifier. |
| | `organization_id` | VARCHAR | FK | Hospital facility where doctor practices. |
| | `doctor_name` | VARCHAR | - | Physician full name. |
| | `specialty` | VARCHAR | - | Medical specialty (*General Practice*, *Cardiology*, etc.). |
| **`stg_organizations`** | `organization_id` | VARCHAR | PK | Hospital facility UUID. |
| | `hospital_name` | VARCHAR | - | Healthcare facility operational name. |
| | `revenue` | NUMBER(12,2) | - | Annual reported facility revenue. |
| **`stg_payors`** | `payor_id` | VARCHAR | PK | Insurance company UUID. |
| | `payor_name` | VARCHAR | - | Health plan name (*Medicare*, *Medicaid*, *Blue Cross*, etc.). |
| **`stg_conditions`** | `encounter_id` | VARCHAR | FK | Associated encounter. |
| | `patient_id` | VARCHAR | FK | Associated patient. |
| | `condition_code` | VARCHAR | - | SNOMED / ICD-10 medical code (`CAST(code AS VARCHAR)`). |
| | `condition_description` | VARCHAR | - | Clinical diagnosis description. |
| **`stg_medications`** | `encounter_id` | VARCHAR | FK | Encounter where prescription was issued. |
| | `medication_code` | VARCHAR | - | RxNorm pharmaceutical code. |
| | `medication_description` | VARCHAR | - | Prescribed drug description. |
| | `total_cost` | NUMBER(12,2) | - | Gross pharmacy cost. |
| **`stg_claims`** | `claim_id` | VARCHAR | PK | Billing claim identifier. |
| | `claim_status` | VARCHAR | - | Claim state (*Approved*, *Pending*, *Rejected*). |

---

### Silver Layer (`HEALTHCARE_DB.SILVER`)

- `dim_patients`: Deduplicated entity table containing unique patient demographic profiles.
- `dim_providers`: Entity table containing physician specialties and facility affiliations.
- `dim_organizations`: Operational master table of hospital facilities.
- `dim_payors`: Insurance carrier reference table.
- `fct_encounters` (Incremental Model):
  - `length_of_stay_hours`: Calculated field `DATEDIFF('hour', start_time, stop_time)`.
  - `patient_out_of_pocket_cost`: Derived calculation `total_claim_cost - payer_coverage`.
- `snapshot_patients` (SCD Type 2): Tracks historical changes with `dbt_valid_from`, `dbt_valid_to`, and `dbt_is_current`.

---

### Gold Layer (`HEALTHCARE_DB.GOLD`)

- `gold_fct_patient_encounters`: Fact table joining encounters with patient demographics, physician specialty, facility name, and insurance payer.
- `gold_dim_patients`: Patient dimension enriched with lifetime metrics (`total_encounters`, `lifetime_claim_cost`, `lifetime_out_of_pocket`, `avg_length_of_stay_hours`).
- `gold_dim_providers`: Provider dimension enriched with practice volume (`total_patients_seen`, `total_encounters_handled`, `total_revenue_generated`).
- `gold_obt_healthcare_analytics` (One Big Table): Single wide denormalized table joining facts, dimensions, diagnoses, and medications for low-latency BI dashboards.

---

## Analytics & Dashboard Metrics

The Executive Analytics Dashboard (`power_bi/dashboard.html`) presents operational and financial metrics across 4 visual sections:

1. Executive Summary:
   - Monthly Patient Encounter Volume: Line chart tracking seasonal hospital admission trends (`GROUP BY SUBSTRING(encounter_start_at, 1, 7)`).
   - Encounter Class Breakdown: Doughnut chart showing Emergency vs Wellness vs Inpatient proportions.
   - Top Diagnosed Conditions: Horizontal bar chart identifying primary clinical drivers.

2. Financial & Payer Breakdown:
   - Insurance Payer Performance Matrix: Table displaying Billed Revenue, Payer Coverage, Patient Out-of-Pocket, and Coverage Rate % per insurance carrier.
   - Billed Cost vs Insurance Coverage: Stacked bar chart comparing gross charges against insurance payouts per visit class.
   - Out-of-Pocket Expense by Race: Bar chart evaluating financial burden across demographic groups.

3. Hospital & Physician Metrics:
   - Hospital Facility Revenue Ranking: Ranks facility gross billing performance.
   - Physician Specialty Distribution: Pie chart breaking down patient encounters across doctor specialties.

4. Clinical & Demographics:
   - Patient Demographics: Gender breakdown visual.
   - Top Prescribed Medications: Summary matrix displaying prescription counts and average prescription costs.

---

## Setup & Quickstart Guide

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/raghav-rathi/student-dbt-3nf-data-pipeline.git
cd student-dbt-3nf-data-pipeline
```

### 2. Configure Credentials (`.env`)
Copy `.env.example` to `.env` and enter your credentials:
```bash
cp .env.example .env
```

### 3. Run dbt Build
```bash
cd dbt_project
../venv/bin/dbt build --target dev        # Local DuckDB Run
../venv/bin/dbt build --target snowflake  # Live Snowflake Cloud Run
```

### 4. View Interactive Dashboard
- Executive Dashboard: Open `power_bi/dashboard.html` in your web browser.
