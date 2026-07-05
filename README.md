# 🏥 Hospital 3NF Data Pipeline — DBT + DuckDB

A production-grade data engineering pipeline that demonstrates **Third Normal Form (3NF)** database normalization on a real-world **Hospital Management System** dataset using **DBT (Data Build Tool)** and **DuckDB**.

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        DATA PIPELINE ARCHITECTURE                       │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  📄 raw_hospital_records.csv                                            │
│         │ (Unnormalized, multi-valued attributes)                       │
│         ▼                                                                │
│  ┌─────────────────────────────────────────────┐                        │
│  │          🟤 BRONZE LAYER (Raw Staging)       │                        │
│  │  bronze_raw_hospital                         │                        │
│  │  • 1:1 copy of CSV with type casting        │                        │
│  │  • 10 records, 18 columns                   │                        │
│  └──────────────────┬──────────────────────────┘                        │
│                     │                                                    │
│                     ▼                                                    │
│  ┌─────────────────────────────────────────────┐                        │
│  │        🔵 SILVER LAYER (3NF Normalized)      │                        │
│  │                                               │                       │
│  │  DIMENSION TABLES:                            │                       │
│  │  ├── dim_patients        (10 rows)           │                        │
│  │  ├── dim_doctors          (7 rows)           │                        │
│  │  ├── dim_departments      (7 rows)           │                        │
│  │  ├── dim_diagnoses       (17 rows)           │                        │
│  │  └── dim_medications     (19 rows)           │                        │
│  │                                               │                       │
│  │  JUNCTION TABLES (Many-to-Many):              │                       │
│  │  ├── patient_phones      (16 rows)           │                        │
│  │  ├── patient_doctors     (20 rows)           │                        │
│  │  ├── patient_diagnoses   (20 rows)           │                        │
│  │  └── patient_medications (28 rows)           │                        │
│  │                                               │                       │
│  │  FACT TABLE:                                  │                       │
│  │  └── fact_visits         (19 rows)           │                        │
│  └──────────────────┬──────────────────────────┘                        │
│                     │                                                    │
│                     ▼                                                    │
│  ┌─────────────────────────────────────────────┐                        │
│  │     🟡 GOLD LAYER (Analytics / OBT)          │                        │
│  │  obt_hospital_analytics  (340 rows)          │                        │
│  │  • Denormalized wide table for Power BI     │                        │
│  │  • Joins all dimensions + facts              │                        │
│  └─────────────────────────────────────────────┘                        │
│                     │                                                    │
│                     ▼                                                    │
│  ┌─────────────────────────────────────────────┐                        │
│  │        📊 POWER BI / ANALYTICS               │                        │
│  │  obt_hospital_analytics.csv                  │                        │
│  └─────────────────────────────────────────────┘                        │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## 📋 Problem Statement

A hospital maintains patient records in a **single flat CSV file** where:
- Each patient has **multiple phone numbers** in one cell
- Each patient is assigned **multiple doctors** (comma-separated)
- Each patient has **multiple diagnoses** (ICD codes)
- Each patient is prescribed **multiple medications** with dosages
- Visit history with billing is **stored as comma-separated values**

This **violates 1NF, 2NF, and 3NF** due to:
- **Multi-valued attributes** (repeating groups in single cells)
- **Partial dependencies** (doctor name depends on doctor ID, not on patient)
- **Transitive dependencies** (department name depends on department ID via doctor)

## 🔧 Normalization Steps

### 1NF — Eliminate Repeating Groups
Split comma-separated values into atomic rows using `STRING_SPLIT + UNNEST`.

### 2NF — Remove Partial Dependencies
Create dimension tables where attributes depend on their own primary key:
- `dim_patients` — patient_id → name, DOB, gender
- `dim_doctors` — doctor_id → name, specialization
- `dim_departments` — department_id → name
- `dim_diagnoses` — diagnosis_code → description
- `dim_medications` — medication_id → name

### 3NF — Remove Transitive Dependencies
- Doctor's department (`department_id`) is a foreign key in `dim_doctors`, not stored with patients
- Medication dosage is stored in `patient_medications` junction table (same med can have different dosages)

## 📁 Project Structure

```
├── data/
│   ├── raw_hospital_records.csv        # Source: Unnormalized hospital data
│   └── hospital_dw.duckdb             # DuckDB data warehouse
├── dbt_project/
│   ├── dbt_project.yml                # DBT project configuration
│   ├── profiles.yml                   # DuckDB connection profile
│   └── models/
│       ├── schema.yml                 # Data quality tests (18 tests)
│       ├── bronze/
│       │   └── bronze_raw_hospital.sql
│       ├── silver/
│       │   ├── dim_patients.sql
│       │   ├── dim_doctors.sql
│       │   ├── dim_departments.sql
│       │   ├── dim_diagnoses.sql
│       │   ├── dim_medications.sql
│       │   ├── patient_phones.sql
│       │   ├── patient_doctors.sql
│       │   ├── patient_diagnoses.sql
│       │   ├── patient_medications.sql
│       │   └── fact_visits.sql
│       └── gold/
│           └── obt_hospital_analytics.sql
├── power_bi/
│   └── obt_hospital_analytics.csv     # Gold OBT export for Power BI
└── README.md
```

## 🚀 How to Run

### Prerequisites
- Python 3.9+
- pip

### Setup & Execute
```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install dbt-core dbt-duckdb

# 3. Run the pipeline
cd dbt_project
dbt debug          # Verify connection
dbt run            # Build all 12 models
dbt test           # Run 18 data quality tests
dbt docs generate  # Generate documentation
dbt docs serve     # View interactive lineage graph
```

### Expected Output
```
dbt run:   PASS=12  WARN=0  ERROR=0  TOTAL=12
dbt test:  PASS=18  WARN=0  ERROR=0  TOTAL=18
```

## 🧪 Data Quality Tests (18 Tests)

| Table | Test | Type |
|-------|------|------|
| dim_patients | patient_id | unique, not_null |
| dim_doctors | doctor_id | unique, not_null |
| dim_departments | department_id | unique, not_null |
| dim_diagnoses | diagnosis_code | unique, not_null |
| dim_medications | medication_id | unique, not_null |
| fact_visits | patient_id, visit_date | not_null |
| patient_doctors | patient_id, doctor_id | not_null |
| patient_diagnoses | patient_id, diagnosis_code | not_null |
| patient_medications | patient_id, medication_id | not_null |

## 📊 ER Diagram (3NF)

```
                    ┌─────────────────┐
                    │  dim_departments │
                    ├─────────────────┤
                    │ PK department_id │
                    │    dept_name     │
                    └────────▲────────┘
                             │ FK
                    ┌────────┴────────┐
                    │   dim_doctors    │
                    ├─────────────────┤
                    │ PK doctor_id     │
                    │    doctor_name   │
                    │    specialization│
                    │ FK department_id │
                    └────────▲────────┘
                             │
              ┌──────────────┤
              │              │
    ┌─────────┴──────┐  ┌───┴──────────────┐
    │patient_doctors │  │  dim_patients     │
    ├────────────────┤  ├──────────────────┤
    │FK patient_id   │  │PK patient_id     │
    │FK doctor_id    │  │   patient_name   │
    └────────────────┘  │   patient_dob    │
                        │   patient_gender │
                        └──┬───┬───┬──────┘
                           │   │   │
           ┌───────────────┘   │   └──────────────┐
           │                   │                   │
    ┌──────┴─────────┐  ┌─────┴──────────┐  ┌────┴───────────────┐
    │patient_phones  │  │patient_diagnoses│  │patient_medications │
    ├────────────────┤  ├────────────────┤  ├────────────────────┤
    │FK patient_id   │  │FK patient_id   │  │FK patient_id       │
    │   phone_number │  │FK diagnosis_code│  │FK medication_id    │
    └────────────────┘  └──────┬─────────┘  │   dosage           │
                               │            └───────┬────────────┘
                        ┌──────┴─────────┐         │
                        │ dim_diagnoses  │   ┌─────┴──────────┐
                        ├────────────────┤   │dim_medications │
                        │PK diagnosis_code│   ├────────────────┤
                        │  description   │   │PK medication_id │
                        └────────────────┘   │  medication_name│
                                             └────────────────┘

    ┌───────────────────┐
    │   fact_visits      │
    ├───────────────────┤
    │ FK patient_id      │
    │    visit_date      │
    │    visit_type      │
    │    billing_amount  │
    └───────────────────┘
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Transformation | DBT (Data Build Tool) |
| Data Warehouse | DuckDB (in-process OLAP) |
| Source Data | CSV (Flat File) |
| Testing | DBT Tests (Unique + Not Null) |
| Analytics Export | CSV → Power BI |
| Architecture | Medallion (Bronze → Silver → Gold) |

## 📝 Key Concepts Demonstrated

1. **Database Normalization (1NF → 2NF → 3NF)** — Systematic decomposition of flat data
2. **Medallion Architecture** — Bronze (raw) → Silver (cleaned/normalized) → Gold (analytics-ready)
3. **DBT Transformations** — SQL-based data transformations with dependency management
4. **Data Quality Testing** — Automated uniqueness and null checks on all primary/foreign keys
5. **Many-to-Many Relationships** — Junction tables for patients ↔ doctors, diagnoses, medications
6. **One Big Table (OBT)** — Gold layer denormalized table optimized for BI consumption
7. **DuckDB as Local DW** — Lightweight, embedded OLAP engine (no server needed)

## 📜 License

This project is for educational/interview demonstration purposes.
