#!/usr/bin/env python3
import os
import sys
import subprocess
import duckdb

def run_cmd(cmd, cwd=None):
    print(f"\n[EXEC] {cmd}")
    res = subprocess.run(cmd, shell=True, cwd=cwd)
    if res.returncode != 0:
        print(f"[ERROR] Command failed: {cmd}")
        sys.exit(res.returncode)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    print("=" * 70)
    print(" 🏥 SYNTHEA HEALTHCARE DATA PIPELINE — AUTOMATED EXECUTION")
    print(" Stack: S3/Snowflake Specs + DuckDB Engine + dbt Medallion Architecture")
    print("=" * 70)

    # 1. GENERATE SYNTHEA DATA
    raw_dir = os.path.join(base_dir, "data", "synthea_raw")
    if not os.path.exists(raw_dir) or len(os.listdir(raw_dir)) == 0:
        print("\n[STEP 1] Generating Synthea relational CSV dataset...")
        from scripts.generate_synthea_data import generate_synthea_dataset
        generate_synthea_dataset(raw_dir)
    else:
        print(f"\n[STEP 1] Synthea raw data existing in {raw_dir}")

    # 2. LOAD RAW CSVs INTO STAGING SCHEMA (DuckDB / Snowflake emulation)
    print("\n[STEP 2] Initializing database and staging schemas...")
    db_path = os.path.join(base_dir, "data", "healthcare_dw.duckdb")
    con = duckdb.connect(db_path)
    con.execute("CREATE SCHEMA IF NOT EXISTS main_staging;")
    
    tables = [
        "patients", "encounters", "providers", "organizations",
        "payors", "conditions", "medications", "procedures", "claims"
    ]
    
    for t in tables:
        csv_file = os.path.join(raw_dir, f"{t}.csv")
        stg_table = f"main_staging.raw_{t}"
        con.execute(f"CREATE OR REPLACE TABLE {stg_table} AS SELECT * FROM read_csv_auto('{csv_file}', header=true);")
        cnt = con.execute(f"SELECT COUNT(*) FROM {stg_table}").fetchone()[0]
        print(f"  [+] Loaded {stg_table}: {cnt} rows")
    con.close()

    # 3. RUN dbt SNAPSHOT (SCD Type 2)
    print("\n[STEP 3] Running dbt snapshot (SCD Type 2 patient snapshot)...")
    dbt_dir = os.path.join(base_dir, "dbt_project")
    dbt_bin = os.path.join(base_dir, "venv", "bin", "dbt")
    if not os.path.exists(dbt_bin):
        dbt_bin = "dbt"

    run_cmd(f"{dbt_bin} snapshot", cwd=dbt_dir)

    # 4. RUN dbt MODELS (Bronze -> Silver 3NF + Incremental -> Gold Star Schema)
    print("\n[STEP 4] Executing dbt models (Bronze, Silver, Gold)...")
    run_cmd(f"{dbt_bin} run", cwd=dbt_dir)

    # 5. RUN dbt TESTS
    print("\n[STEP 5] Running 25+ automated dbt data quality & FK relationship tests...")
    run_cmd(f"{dbt_bin} test", cwd=dbt_dir)

    # 6. EXPORT GOLD OBT TO CSV FOR POWER BI
    print("\n[STEP 6] Exporting Gold OBT table to CSV for Power BI...")
    power_bi_dir = os.path.join(base_dir, "power_bi")
    os.makedirs(power_bi_dir, exist_ok=True)
    csv_out = os.path.join(power_bi_dir, "gold_obt_healthcare_analytics.csv")
    
    con = duckdb.connect(db_path)
    df = con.execute("SELECT * FROM main_gold.gold_obt_healthcare_analytics").df()
    df.to_csv(csv_out, index=False)
    print(f"  [+] Exported {len(df)} rows to {csv_out}")

    print("\n" + "=" * 70)
    print(" SUCCESS! ALL DBT MODELS & DATA QUALITY TESTS PASSED (100%)")
    print("=" * 70)

if __name__ == "__main__":
    main()
