# 🏥 Synthea Healthcare Data Pipeline & Analytics (AWS S3 + Snowflake + dbt)

An end-to-end, enterprise-grade Data Engineering and Analytics project building a **Medallion Data Pipeline (Bronze → Silver 3NF → Gold Star Schema)** on the **Synthea™ Healthcare Relational Dataset** using **AWS S3**, **Snowflake**, **dbt (Data Build Tool)**, and **Power BI**.

---

## 🏗️ Architecture Overview

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
│     • 24 dbt automated data quality & FK relationship tests                                 │
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

## 🔑 Key Features Demonstrated

1. **Relational Data Modeling (3NF → Star Schema)**:
   - Evaluated 9 normalized Synthea relational tables (`patients`, `encounters`, `providers`, `organizations`, `payors`, `conditions`, `medications`, `procedures`, `claims`).
   - Converted 3NF database model into a **Business Star Schema** with conformed dimensions.

2. **Incremental Materialization Strategy (`fct_encounters`)**:
   - Configured high-volume transactional encounters as `materialized='incremental'`.
   - Utilized Snowflake `MERGE` upsert strategy with a **3-day lookback window** (`is_incremental()`) to handle late-arriving billing updates without full-table scans.

3. **Slowly Changing Dimensions (SCD Type 2)**:
   - Built `snapshots/snapshot_patients.sql` using `dbt snapshot` to preserve patient demographic and insurance history over time (`dbt_valid_from`, `dbt_valid_to`, `dbt_is_current`).

4. **Automated Data Quality & FK Relationship Testing**:
   - 24 automated dbt tests enforcing PK uniqueness, non-null constraints, and referential foreign key integrity across all silver and gold tables.

5. **Power BI Executive Dashboard Integration**:
   - Exported `gold_obt_healthcare_analytics.csv` designed for a **4-Tab Executive Power BI Dashboard** (Executive Command Center, Financial & Payer Analysis, Provider Operations, Clinical Deep-Dive).

---

## 📂 Repository File Structure

```text
├── DDL/
│   └── snowflake_setup.sql             # Snowflake Storage Integration, Stage, & COPY DDL
├── data/
│   └── synthea_raw/                    # 9 Raw Synthea CSV files
├── dbt_project/
│   ├── dbt_project.yml                 # dbt project configuration
│   ├── profiles.yml                    # Snowflake & DuckDB profiles
│   ├── models/
│   │   ├── sources/
│   │   │   └── sources.yml             # Raw staging tables definition
│   │   ├── bronze/                     # 9 Staging Views (`stg_*`)
│   │   ├── silver/                     # 3NF Cleaned Models (`dim_*`, `fct_*`)
│   │   └── gold/                       # Star Schema & BI OBT (`gold_*`)
│   ├── snapshots/
│   │   └── snapshot_patients.sql       # SCD Type 2 Snapshot
│   └── tests/                          # 24 dbt Data Quality & FK Relationship Tests
├── power_bi/
│   └── gold_obt_healthcare_analytics.csv # Exported OBT for Power BI
├── scripts/
│   └── generate_synthea_data.py        # Synthea relational CSV data generator
├── .env.example                        # Template for AWS & Snowflake credentials
├── SETUP_CREDENTIALS.md                # Step-by-step credentials guide
├── PROPOSAL_PLAN.md                    # Complete technical proposal document
├── run_pipeline.py                     # Master 1-click execution script
└── README.md                           # Repository documentation
```

---

## 🚀 How to Run the Pipeline

### Option 1: Automated 1-Click Execution (Local Mode)
Run the master pipeline script:
```bash
./run_pipeline.py
```
This script will automatically:
1. Generate the Synthea relational dataset in `data/synthea_raw/`.
2. Initialize the database and staging schemas.
3. Run `dbt snapshot` (building SCD Type 2 patient snapshot).
4. Run `dbt run` (building Bronze views, Silver 3NF, and Gold Star Schema).
5. Run `dbt test` (verifying 24 PK/FK relationship tests).
6. Export `gold_obt_healthcare_analytics.csv` to `power_bi/`.

### Option 2: Live Cloud Deployment (AWS S3 + Snowflake)
1. Copy `.env.example` to `.env` and enter your AWS & Snowflake credentials:
   ```bash
   cp .env.example .env
   ```
2. Execute `DDL/snowflake_setup.sql` in Snowflake Snowsight.
3. Run dbt targetting Snowflake:
   ```bash
   cd dbt_project
   dbt snapshot --target snowflake
   dbt run --target snowflake
   dbt test --target snowflake
   ```

---

## 🧪 Automated Test Verification

All 24 dbt quality tests pass 100%:

```text
Done. PASS=24 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=24
```

- `unique` and `not_null` tests on all Primary Keys.
- `relationships` tests enforcing Foreign Keys (`fct_encounters.patient_id` → `dim_patients.patient_id`, etc.).

---

## 📜 License

Educational and professional demonstration project.
