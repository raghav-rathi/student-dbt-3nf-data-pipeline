# 🏥 Enterprise Healthcare Analytics & Medallion Data Pipeline

> **End-to-End Data Engineering & Business Intelligence Project**  
> Built with **AWS S3**, **Snowflake Data Warehouse**, **dbt (data build tool)**, **SCD Type 2 Snapshots**, **Incremental Loading**, and an **Executive Analytics Dashboard**.

---

## 📌 Executive Table of Contents
1. [Project Overview & Key Highlights](#-project-overview--key-highlights)
2. [End-to-End System Architecture](#-end-to-end-system-architecture)
3. [Key Architectural & Technical Decisions](#-key-architectural--technical-decisions)
4. [Complete Data Dictionary & Schema Reference](#-complete-data-dictionary--schema-reference)
5. [Analytics Extraction & Dashboard Design Logic](#-analytics-extraction--dashboard-design-logic)
6. [Comprehensive Technical Interview Q&A Guide](#-comprehensive-technical-interview-qa-guide)
7. [Quickstart Guide (Run locally or in Snowflake)](#-quickstart-guide)

---

## 🚀 Project Overview & Key Highlights

This enterprise data pipeline ingests synthetic electronic health record (EHR) data from **Synthea™**, processes it through an **AWS S3 Data Lake**, loads it into **Snowflake Data Warehouse**, and transforms it using **dbt** into a 3NF Medallion Data Architecture (Bronze → Silver 3NF → Gold Star Schema).

### Key Accomplishments:
- ☁️ **AWS S3 Landing Zone**: Automated multi-file upload of 9 raw healthcare entities (`patients`, `encounters`, `providers`, `organizations`, `payors`, `conditions`, `medications`, `procedures`, `claims`).
- ❄️ **Snowflake Data Warehouse**: Production database setup (`HEALTHCARE_DB`) with bulk `COPY INTO` staging tables.
- 🟤 **Bronze Layer**: 9 standardized staging views with ISO timestamp parsing, header normalization, and string trimming.
- 🔵 **Silver Layer (3NF & Advanced Engineering)**:
  - **Third Normal Form (3NF)** relational database design reducing redundancy and data anomalies.
  - **Incremental Materialization**: High-volume `fct_encounters` table uses `is_incremental()` with a 3-day lookback window & Snowflake `MERGE`.
  - **Slowly Changing Dimension (SCD Type 2)**: Historical tracking of patient demographic/insurance updates in `snapshots/snapshot_patients.sql` (`dbt_valid_from`, `dbt_valid_to`, `dbt_is_current`).
- 🥇 **Gold Layer (Star Schema & OBT)**:
  - Dimensional models (`gold_dim_patients`, `gold_dim_providers`) + Fact model (`gold_fct_patient_encounters`).
  - **One Big Table (OBT)** wide table (`gold_obt_healthcare_analytics`) optimized for low-latency BI queries.
- ✅ **Data Quality Test Suite**: 24 automated dbt tests validating primary key uniqueness, non-null constraints, and foreign key referential integrity (**100% PASS** rate).
- 📊 **Executive Analytics Dashboard**: Clean, human-crafted HTML5/CSS3/Chart.js interactive dashboard with dynamic filters for facility, payer, and visit class.
- 🌐 **Interactive dbt Lineage Graph**: Self-contained DAG visualization website (`dbt_lineage_docs.html`).

---

## 🏗️ End-to-End System Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   SYSTEM ARCHITECTURE DIAGRAM                               │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│   [ Raw Synthea CSV Files ] (9 Entities)                                                     │
│              │                                                                              │
│              ▼                                                                              │
│   [ Python Boto3 Uploader ] ──► [ AWS S3 Bucket: s3://healthcare-pipeline-harsh/raw/ ]      │
│                                           │                                                 │
│                                           ▼ (Snowflake COPY INTO)                           │
│                             [ Snowflake DW: HEALTHCARE_DB ]                                 │
│                                           │                                                 │
│  ┌────────────────────────────────────────┴──────────────────────────────────────────────┐ │
│  │                              dbt MEDALLION TRANSFORMATIONS                               │ │
│  ├──────────────────────────────────────────────────────────────────────────────────────────┤ │
│  │                                                                                          │ │
│  │  🟤 BRONZE SCHEMA (Views)                                                                 │ │
│  │     stg_patients, stg_encounters, stg_providers, stg_organizations, stg_payors,          │ │
│  │     stg_conditions, stg_medications, stg_procedures, stg_claims                         │ │
│  │                                 │                                                        │ │
│  │                                 ▼                                                        │ │
│  │  ⏳ SNAPSHOTS SCHEMA (SCD Type 2)                                                         │ │
│  │     snapshot_patients (dbt_valid_from, dbt_valid_to, dbt_is_current)                     │ │
│  │                                 │                                                        │ │
│  │                                 ▼                                                        │ │
│  │  🔵 SILVER SCHEMA (3NF Relational Tables)                                                 │ │
│  │     dim_patients, dim_providers, dim_organizations, dim_payors                            │ │
│  │     fct_encounters (Incremental), fct_claims, fct_medications, fct_procedures,           │ │
│  │     fct_conditions                                                                       │ │
│  │                                 │                                                        │ │
│  │                                 ▼                                                        │ │
│  │  🥇 GOLD SCHEMA (Star Schema & OBT)                                                      │ │
│  │     gold_fct_patient_encounters, gold_dim_patients, gold_dim_providers                   │ │
│  │     gold_obt_healthcare_analytics (Wide Denormalized Analytics Table)                    │ │
│  │                                                                                          │ │
│  └────────────────────────────────────────┬─────────────────────────────────────────────────┘ │
│                                           │                                                 │
│                                           ▼                                                 │
│                    [ Executive Analytics Dashboard (dashboard.html) ]                        │
│                     [ Power BI Report Dataset (obt_analytics.csv) ]                         │
│                     [ Interactive dbt Lineage DAG (dbt_docs.html) ]                         │
│                                                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 💡 Key Architectural & Technical Decisions

### 1. Why AWS S3 as the Data Lake Storage Layer?
- **Decoupling Ingestion from Compute**: Landing raw CSV files in AWS S3 isolates the source generation process from downstream database compute.
- **Auditability & Replayability**: Retaining immutable raw CSV files in S3 allows reprocessing or backfilling historical data at any time without re-running data generators.

### 2. Why Snowflake as the Enterprise Cloud Data Warehouse?
- **Separation of Storage & Compute**: Allows virtual warehouses (`COMPUTE_WH`) to scale up or auto-suspend independently of database storage costs.
- **Micro-Partitioning & Pruning**: Snowflake automatically partitions data by insertion time, allowing fast query execution on large datasets.
- **RSA Key-Pair Authentication**: Replaced standard password login with RSA Private Key authentication (`snowflake_key.p8`), ensuring secure, headless CI/CD execution without password prompt blockers.

### 3. Why Medallion Architecture (Bronze → Silver 3NF → Gold Star Schema)?
- **Bronze (Raw/Staging Views)**: Standardizes data types (casting ISO strings to `TIMESTAMP`/`DATE`), normalizes column names to `snake_case`, and applies `TRIM()` to prevent joining errors.
- **Silver (3NF Relational Core)**: Enforces **Third Normal Form (3NF)** to eliminate data redundancy and preserve relational integrity across entities (`patients`, `providers`, `organizations`, `payors`).
- **Gold (Star Schema & OBT)**: Pre-aggregates dimensions and metrics into a denormalized **One Big Table (OBT)** wide dataset (`gold_obt_healthcare_analytics`), eliminating multi-table JOIN latency for executive BI reporting.

### 4. Why Incremental Materialization (`fct_encounters`)?
- **Problem**: Full-table refreshes on millions of healthcare encounters become cost-prohibitive and slow.
- **Solution**: Implemented `materialized='incremental'` in dbt with a **3-day lookback window**:
  ```sql
  {% if is_incremental() %}
    WHERE encounter_start_at >= (
        SELECT COALESCE(MAX(encounter_start_at), CAST('1970-01-01' AS TIMESTAMP)) FROM {{ this }}
    ) - INTERVAL '3 days'
  {% endif %}
  ```
- **Benefit**: Uses Snowflake `MERGE` to insert new encounter records and update existing late-arriving billing claims while scanning only recent data micro-partitions.

### 5. Why Slowly Changing Dimensions (SCD Type 2) for Patients?
- **Problem**: Patients change addresses or insurance providers over time. Overwriting historical records distorts past financial audit trails.
- **Solution**: Created `snapshots/snapshot_patients.sql` using `dbt snapshot` with `strategy='timestamp'` and `updated_at='updated_at'`.
- **Benefit**: Appends new rows whenever patient attributes change, populating `dbt_valid_from`, `dbt_valid_to`, and `dbt_is_current`. Point-in-time joins in Gold models maintain accurate historical reporting.

---

## 📖 Complete Data Dictionary & Schema Reference

### 🟤 Bronze Layer (Staging Views in `HEALTHCARE_DB.BRONZE`)

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

### 🔵 Silver Layer (3NF Relational Tables in `HEALTHCARE_DB.SILVER`)

- **`dim_patients`**: Deduplicated entity table containing unique patient demographic profiles.
- **`dim_providers`**: Entity table containing physician specialties and facility affiliations.
- **`dim_organizations`**: Operational master table of hospital facilities.
- **`dim_payors`**: Insurance carrier reference table.
- **`fct_encounters` (Incremental Model)**:
  - **`length_of_stay_hours`**: Calculated field `DATEDIFF('hour', start_time, stop_time)`.
  - **`patient_out_of_pocket_cost`**: Derived calculation `total_claim_cost - payer_coverage`.
- **`snapshot_patients` (SCD Type 2)**: Tracks historical changes with `dbt_valid_from`, `dbt_valid_to`, and `dbt_is_current`.

---

### 🥇 Gold Layer (Star Schema & OBT in `HEALTHCARE_DB.GOLD`)

- **`gold_fct_patient_encounters`**: Fact table joining encounters with patient demographics, physician specialty, facility name, and insurance payer.
- **`gold_dim_patients`**: Patient dimension enriched with lifetime metrics (`total_encounters`, `lifetime_claim_cost`, `lifetime_out_of_pocket`, `avg_length_of_stay_hours`).
- **`gold_dim_providers`**: Provider dimension enriched with practice volume (`total_patients_seen`, `total_encounters_handled`, `total_revenue_generated`).
- **`gold_obt_healthcare_analytics` (One Big Table)**: Single wide denormalized table joining facts, dimensions, diagnoses, and medications for low-latency BI dashboards.

---

## 📊 Analytics Extraction & Dashboard Design Logic

The **Executive Analytics Dashboard** (`power_bi/dashboard.html`) was designed using a clean, human-crafted layout.

### 4 Executive Visual Tabs:

1. **Executive Summary**:
   - **Monthly Patient Encounter Volume**: Line chart tracking seasonal hospital admission trends (`GROUP BY SUBSTRING(encounter_start_at, 1, 7)`).
   - **Encounter Class Breakdown**: Doughnut chart showing Emergency vs Wellness vs Inpatient proportions.
   - **Top Diagnosed Conditions**: Horizontal bar chart identifying primary clinical drivers.

2. **Financial & Payer Breakdown**:
   - **Insurance Payer Performance Matrix**: Table showing `Billed Revenue`, `Payer Coverage`, `Patient Out-of-Pocket`, and `Coverage Rate %` per insurance company.
   - **Billed Cost vs Insurance Coverage**: Stacked bar chart comparing gross charges against insurance payouts per visit class.
   - **Out-of-Pocket Expense by Race**: Bar chart evaluating financial burden across demographic groups.

3. **Hospital & Physician Metrics**:
   - **Hospital Facility Revenue Ranking**: Ranks facility gross billing performance.
   - **Physician Specialty Distribution**: Pie chart breaking down patient encounters across doctor specialties.

4. **Clinical & Demographics**:
   - **Patient Demographics**: Gender breakdown visual.
   - **Top Prescribed Medications**: Summary matrix displaying prescription counts and average prescription costs.

---

## 🗣️ Comprehensive Technical Interview Q&A Guide

### Q1: Can you walk me through your pipeline's end-to-end data architecture?
> *"I designed a Medallion data pipeline where raw Synthea EHR CSV files are uploaded to an AWS S3 data lake via Python boto3. From S3, raw data is ingested into Snowflake staging using bulk `COPY INTO`. Using dbt, I transformed the raw data into Bronze staging views, Silver 3NF relational tables, an SCD Type 2 patient snapshot, and a Gold Star Schema OBT wide table. Finally, analytical insights are rendered through an interactive Executive Web Dashboard."*

### Q2: Why did you choose 3NF for the Silver layer instead of jumping straight to a Star Schema?
> *"The Silver layer serves as the single source of truth for operational systems. Third Normal Form (3NF) eliminates data redundancy, ensures referential integrity, and prevents insertion/update/deletion anomalies. Once Silver 3NF is established, building downstream Gold Star Schemas for BI becomes straightforward and consistent."*

### Q3: How did you implement Incremental Loading in dbt, and why is it important?
> *"For high-volume transaction models like `fct_encounters`, full table rebuilds are expensive. I implemented `materialized='incremental'` using dbt's `is_incremental()` macro with a 3-day lookback window. When executed, dbt generates a Snowflake `MERGE` statement that inserts new records and updates modified claims without scanning historical data."*

### Q4: How do you handle Slowly Changing Dimensions (SCD Type 2)?
> *"To preserve historical accuracy when patient addresses or insurance coverage change, I built `snapshots/snapshot_patients.sql` using `dbt snapshot`. dbt tracks changes using the `updated_at` timestamp, automatically populating `dbt_valid_from`, `dbt_valid_to`, and `dbt_is_current` columns."*

### Q5: How did you handle authentication security for automated dbt runs?
> *"Instead of storing plaintext passwords or relying on browser authentication, I configured Snowflake RSA Key-Pair Authentication (`snowflake_key.p8`). I assigned the public key to the Snowflake user and configured `private_key_path` in `profiles.yml`, enabling headless execution."*

### Q6: How do you ensure data quality across your pipeline?
> *"I built a test suite with 24 automated dbt tests in `schema.yml`. These tests enforce `unique` primary keys, `not_null` constraints on critical fields, and `relationships` (foreign key integrity) between fact tables and dimension tables."*

---

## 🛠️ Quickstart Guide

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

### 4. View Interactive Dashboards
- **Executive Dashboard**: Double-click [power_bi/dashboard.html](file:///Users/whiterose/Downloads/HarshProject/power_bi/dashboard.html).
- **dbt Lineage Graph DAG**: Double-click [dbt_project/dbt_lineage_docs.html](file:///Users/whiterose/Downloads/HarshProject/dbt_project/dbt_lineage_docs.html).
