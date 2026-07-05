import os
import sys
import subprocess
from dotenv import load_dotenv

load_dotenv()

def run_cmd(cmd, cwd=None):
    print(f"\n[EXEC] {cmd}")
    env = os.environ.copy()
    res = subprocess.run(cmd, shell=True, cwd=cwd, env=env)
    if res.returncode != 0:
        print(f"[ERROR] Command failed with exit code {res.returncode}")
        sys.exit(res.returncode)

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dbt_dir = os.path.join(base_dir, "dbt_project")
    dbt_bin = os.path.join(base_dir, "venv", "bin", "dbt")

    print("=" * 70)
    print(" ❄️ RUNNING DBT PIPELINE DIRECTLY ON LIVE SNOWFLAKE CLOUD")
    print(f" Account: {os.getenv('SNOWFLAKE_ACCOUNT')} | User: {os.getenv('SNOWFLAKE_USER')}")
    print("=" * 70)

    # 1. dbt Debug
    print("\n[STEP 1] Testing Snowflake Connection...")
    run_cmd(f"{dbt_bin} debug --target snowflake", cwd=dbt_dir)

    # 2. dbt Snapshot (SCD Type 2)
    print("\n[STEP 2] Building SCD Type 2 Patients Snapshot in Snowflake...")
    run_cmd(f"{dbt_bin} snapshot --target snowflake", cwd=dbt_dir)

    # 3. dbt Run (Bronze, Silver 3NF, Gold Star Schema)
    print("\n[STEP 3] Building Bronze, Silver 3NF, and Gold Star Schema in Snowflake...")
    run_cmd(f"{dbt_bin} run --target snowflake", cwd=dbt_dir)

    # 4. dbt Test (24 Quality & Relationship Tests)
    print("\n[STEP 4] Executing 24 Automated Data Quality & FK Tests in Snowflake...")
    run_cmd(f"{dbt_bin} test --target snowflake", cwd=dbt_dir)

    print("\n" + "=" * 70)
    print(" 🎉 SUCCESS! ALL DBT MODELS & TESTS PASSED ON LIVE SNOWFLAKE (100%)")
    print("=" * 70)

if __name__ == "__main__":
    main()
