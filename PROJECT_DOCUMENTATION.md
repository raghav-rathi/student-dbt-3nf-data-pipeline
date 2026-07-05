# 🏥 Comprehensive Healthcare Analytics & Medallion Data Pipeline Guide

This document provides a comprehensive technical breakdown of the **Healthcare Data Pipeline**, including architecture diagrams, design decisions, data dictionaries, query logic, and interview preparation questions.

---

## 🏛️ Architecture Overview

The system processes raw electronic health record (EHR) data from **Synthea™** through a **3-tier Medallion Data Architecture**:

1. **Ingestion Layer**: Raw CSV files landed in **AWS S3** (`s3://healthcare-pipeline-harsh/raw/`).
2. **Warehouse Layer**: Staged in **Snowflake Data Warehouse** (`HEALTHCARE_DB.STAGING`).
3. **Transformation Layer (dbt)**:
   - **Bronze**: Standardized staging views (`HEALTHCARE_DB.BRONZE`).
   - **Silver (3NF)**: Normalized relational core (`HEALTHCARE_DB.SILVER`).
   - **Snapshots (SCD Type 2)**: Historical attribute tracking (`HEALTHCARE_DB.SNAPSHOTS`).
   - **Gold (Star Schema / OBT)**: Analytical facts and OBT wide table (`HEALTHCARE_DB.GOLD`).
4. **Presentation Layer**: Executive Web Dashboard (`power_bi/dashboard.html`) and Power BI OBT Dataset.

---

## 📖 Schema & Data Dictionary

### Bronze Staging Layer (`HEALTHCARE_DB.BRONZE`)
- **`stg_patients`**: Cleaned patient master data (`patient_id`, `first_name`, `last_name`, `gender`, `race`, `ethnicity`, `birth_date`, `address`, `insurance_provider`, `updated_at`).
- **`stg_encounters`**: Cleaned hospital visit records (`encounter_id`, `start_time`, `stop_time`, `patient_id`, `organization_id`, `provider_id`, `payor_id`, `encounter_class`, `total_claim_cost`, `payer_coverage`).
- **`stg_providers`**: Physician directory (`provider_id`, `organization_id`, `doctor_name`, `gender`, `specialty`, `address`).
- **`stg_organizations`**: Hospital facility directory (`organization_id`, `hospital_name`, `address`, `phone`, `revenue`).
- **`stg_payors`**: Insurance company directory (`payor_id`, `payor_name`, `address`, `phone`).
- **`stg_conditions`**: Patient clinical diagnoses (`onset_date`, `patient_id`, `encounter_id`, `condition_code`, `condition_description`).
- **`stg_medications`**: Prescribed pharmaceuticals (`start_time`, `patient_id`, `encounter_id`, `medication_code`, `medication_description`, `total_cost`).
- **`stg_procedures`**: Medical treatments administered (`start_time`, `patient_id`, `encounter_id`, `procedure_code`, `procedure_description`).
- **`stg_claims`**: Insurance billing claims (`claim_id`, `patient_id`, `provider_id`, `claim_status`, `service_date`).

### Silver 3NF Core (`HEALTHCARE_DB.SILVER`)
- **`dim_patients`**: Unique patient dimension table.
- **`dim_providers`**: Unique doctor dimension table.
- **`dim_organizations`**: Unique hospital dimension table.
- **`dim_payors`**: Unique payer dimension table.
- **`fct_encounters`**: Core encounter fact table enriched with `length_of_stay_hours` and `patient_out_of_pocket_cost`.
- **`snapshot_patients`**: SCD Type 2 table tracking patient changes over time (`dbt_valid_from`, `dbt_valid_to`, `dbt_is_current`).

### Gold Star Schema (`HEALTHCARE_DB.GOLD`)
- **`gold_fct_patient_encounters`**: Denormalized encounter fact table joined with patient, provider, hospital, and payer attributes.
- **`gold_dim_patients`**: Patient profile enriched with lifetime metrics (`total_encounters`, `lifetime_claim_cost`, `lifetime_out_of_pocket`, `avg_length_of_stay_hours`).
- **`gold_dim_providers`**: Doctor profile enriched with clinical metrics (`total_patients_seen`, `total_encounters_handled`, `total_revenue_generated`).
- **`gold_obt_healthcare_analytics`**: Single One Big Table (OBT) wide dataset combining all facts, dimensions, diagnoses, and medications for low-latency BI analytics.

---

## 🗣️ Key Interview Preparation Summary

### 1. Why 3NF in Silver?
Normalizing data into 3NF in Silver eliminates redundancies and update anomalies, creating an enterprise single source of truth before building dimensional Gold models.

### 2. How does Incremental MERGE work?
`fct_encounters` uses `materialized='incremental'` with a 3-day lookback window (`WHERE encounter_start_at >= MAX(encounter_start_at) - INTERVAL '3 days'`). dbt compiles this into a native Snowflake `MERGE` statement, updating existing records and inserting new ones without re-scanning the entire table.

### 3. How does SCD Type 2 work?
`snapshot_patients` monitors changes in patient address or insurance provider. When a change occurs, dbt closes out the old row (`dbt_valid_to = current_timestamp`, `dbt_is_current = false`) and inserts a new active row (`dbt_is_current = true`).

### 4. How was security handled?
We implemented RSA Key-Pair Authentication (`snowflake_key.p8`), eliminating plaintext passwords and bypassing interactive MFA prompts during automated dbt execution.
