# 📊 Complete Healthcare Analytics & SQL Query Interview Guide

This guide explains the end-to-end data pipeline flow, SQL query logic, and analytical transformations used to build the **Executive Healthcare Analytics Dashboard**.

---

## 🏗️ 1. The Data Lineage Story (How Data Got to the Dashboard)

```text
  📄 Synthea Raw CSVs (9 Tables)
        │
        ▼ (AWS CLI / boto3 Python Uploader)
  ☁️ AWS S3 Bucket (`s3://healthcare-pipeline-harsh/raw/`)
        │
        ▼ (Snowflake `COPY INTO` DDL)
  ❄️ Snowflake Raw Staging Schema (`HEALTHCARE_DB.STAGING.RAW_*`)
        │
        ▼ (dbt Bronze Staging Views)
  🟤 `stg_patients`, `stg_encounters`, `stg_providers`, `stg_organizations`, etc.
        │
        ▼ (dbt Silver 3NF Cleaned Models + Incremental + SCD Type 2 Snapshots)
  🔵 `dim_patients`, `dim_providers`, `snapshot_patients`, `fct_encounters` (Incremental)
        │
        ▼ (dbt Gold Star Schema)
  🥇 `gold_fct_patient_encounters`, `gold_dim_patients`, `gold_dim_providers`
        │
        ▼ (dbt Gold One Big Table - OBT Export)
  🟡 `gold_obt_healthcare_analytics.csv`
        │
        ▼ (Dashboard Engine & Chart.js)
  📊 Executive Healthcare Analytics Dashboard (`power_bi/dashboard.html`)
```

---

## 🧮 2. SQL Query Logic for Each Dashboard Visual

### 🟢 Top Header KPI Cards
- **Total Encounters**:
  ```sql
  SELECT COUNT(DISTINCT encounter_id) FROM gold_obt_healthcare_analytics;
  ```
- **Total Billed Claims Revenue**:
  ```sql
  SELECT SUM(total_claim_cost) FROM gold_obt_healthcare_analytics;
  ```
- **Insurance Payer Coverage Rate %**:
  ```sql
  SELECT ROUND(SUM(payer_coverage) / SUM(total_claim_cost) * 100, 1) FROM gold_obt_healthcare_analytics;
  ```
- **Avg Patient Out-of-Pocket Cost**:
  ```sql
  SELECT ROUND(AVG(patient_out_of_pocket_cost), 2) FROM gold_obt_healthcare_analytics;
  ```
- **Avg Length of Stay (LOS)**:
  ```sql
  SELECT ROUND(AVG(length_of_stay_hours), 1) FROM gold_obt_healthcare_analytics;
  ```

---

### 📈 Tab 1: Executive KPI Command Center

#### Visual 1: Monthly Encounter & Revenue Trend
- **Purpose**: Tracks seasonal changes in hospital visit volume and revenue over time.
- **SQL Logic**:
  ```sql
  SELECT 
      SUBSTRING(encounter_start_at, 1, 7) AS encounter_month,
      COUNT(encounter_id) AS total_encounters,
      SUM(total_claim_cost) AS total_revenue
  FROM gold_obt_healthcare_analytics
  GROUP BY 1
  ORDER BY 1 ASC;
  ```

#### Visual 2: Encounter Class Breakdown
- **Purpose**: Shows the distribution of visit types (*Emergency*, *Inpatient*, *Wellness*, *Ambulatory*, *Urgentcare*).
- **SQL Logic**:
  ```sql
  SELECT 
      encounter_class,
      COUNT(encounter_id) AS encounter_count
  FROM gold_obt_healthcare_analytics
  GROUP BY 1
  ORDER BY 2 DESC;
  ```

#### Visual 3: Top 5 Diagnosed Medical Conditions
- **Purpose**: Identifies the primary clinical drivers of hospital admissions.
- **SQL Logic**:
  ```sql
  SELECT 
      condition_description,
      COUNT(encounter_id) AS diagnosis_count
  FROM gold_obt_healthcare_analytics
  WHERE condition_description IS NOT NULL
  GROUP BY 1
  ORDER BY 2 DESC
  LIMIT 5;
  ```

---

### 💰 Tab 2: Financial & Insurance Payer Analytics

#### Visual 1: Insurance Payer Financial Performance Matrix
- **Purpose**: Evaluates how much revenue each insurance company generates vs how much out-of-pocket burden falls on patients.
- **SQL Logic**:
  ```sql
  SELECT 
      payor_name,
      COUNT(encounter_id) AS total_encounters,
      ROUND(SUM(total_claim_cost), 2) AS billed_revenue,
      ROUND(SUM(payer_coverage), 2) AS payer_payout,
      ROUND(SUM(patient_out_of_pocket_cost), 2) AS patient_copay,
      ROUND(SUM(payer_coverage) / SUM(total_claim_cost) * 100, 1) AS coverage_rate_pct
  FROM gold_obt_healthcare_analytics
  GROUP BY payor_name
  ORDER BY billed_revenue DESC;
  ```

#### Visual 2: Billed Cost vs Insurance Coverage by Visit Class
- **Purpose**: Compares total hospital charges against actual insurance reimbursement per visit category.
- **SQL Logic**:
  ```sql
  SELECT 
      encounter_class,
      ROUND(SUM(total_claim_cost), 2) AS total_billed,
      ROUND(SUM(payer_coverage), 2) AS total_covered
  FROM gold_obt_healthcare_analytics
  GROUP BY 1;
  ```

#### Visual 3: Patient Financial Burden by Demographics (Race)
- **Purpose**: Analyzes average out-of-pocket medical expenses across patient demographic groups.
- **SQL Logic**:
  ```sql
  SELECT 
      patient_race,
      ROUND(AVG(patient_out_of_pocket_cost), 2) AS avg_out_of_pocket
  FROM gold_obt_healthcare_analytics
  GROUP BY 1
  ORDER BY 2 DESC;
  ```

---

### 🏥 Tab 3: Hospital & Physician Operational Performance

#### Visual 1: Hospital Facility Revenue Ranking
- **Purpose**: Ranks hospital organizations by gross billed claim revenue.
- **SQL Logic**:
  ```sql
  SELECT 
      hospital_name,
      COUNT(encounter_id) AS total_visits,
      ROUND(SUM(total_claim_cost), 2) AS total_revenue
  FROM gold_obt_healthcare_analytics
  GROUP BY 1
  ORDER BY total_revenue DESC;
  ```

#### Visual 2: Physician Specialty Workload Distribution
- **Purpose**: Shows patient encounter volume distributed across doctor specialties.
- **SQL Logic**:
  ```sql
  SELECT 
      doctor_specialty,
      COUNT(encounter_id) AS encounter_count
  FROM gold_obt_healthcare_analytics
  GROUP BY 1
  ORDER BY 2 DESC;
  ```

---

### 🩺 Tab 4: Clinical & Demographic Deep-Dive

#### Visual 1: Patient Gender Distribution
- **SQL Logic**:
  ```sql
  SELECT 
      patient_gender,
      COUNT(DISTINCT patient_id) AS patient_count
  FROM gold_obt_healthcare_analytics
  GROUP BY 1;
  ```

#### Visual 2: Top Prescribed Medications Summary Table
- **SQL Logic**:
  ```sql
  SELECT 
      medication_description,
      COUNT(encounter_id) AS prescription_count,
      ROUND(AVG(total_claim_cost), 2) AS avg_cost
  FROM gold_obt_healthcare_analytics
  WHERE medication_description IS NOT NULL
  GROUP BY 1
  ORDER BY 2 DESC
  LIMIT 8;
  ```

---

## 💡 Key Technical Concept Summary for Interviews

1. **Why Medallion Architecture?**
   - **Bronze (Staging)**: Raw copy with standardized data types and naming.
   - **Silver (3NF)**: Cleaned, normalized enterprise model separating entities from transactions.
   - **Gold (Star Schema / OBT)**: Analytical facts and wide table optimized for BI.

2. **Why Incremental (`fct_encounters`)?**
   - Uses `is_incremental()` and a 3-day lookback window (`WHERE encounter_start_at >= MAX(encounter_start_at) - INTERVAL '3 days'`) to process only new/updated records without expensive full-table scans.

3. **Why SCD Type 2 (`snapshot_patients`)?**
   - Uses `dbt snapshot` to track patient address and insurance changes over time (`dbt_valid_from`, `dbt_valid_to`, `dbt_is_current`), enabling historical point-in-time reporting.

4. **Data Quality Tests**:
   - 24 automated dbt tests enforcing PK uniqueness, non-null fields, and FK referential integrity (`relationships`).
