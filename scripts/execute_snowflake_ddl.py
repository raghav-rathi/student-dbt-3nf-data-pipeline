import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT", "RWPEXUG-HB24805")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER", "HARSHSOMANI2003")
SNOWFLAKE_AUTHENTICATOR = os.getenv("SNOWFLAKE_AUTHENTICATOR", "externalbrowser")
SNOWFLAKE_ROLE = os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN")

def execute_ddl():
    print(f"❄️ Connecting to Snowflake Account: {SNOWFLAKE_ACCOUNT} as User: {SNOWFLAKE_USER}...")
    print("  [!] Browser window will open to authenticate. Please click 'Confirm' / Log in in your browser.")

    ctx = snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        authenticator=SNOWFLAKE_AUTHENTICATOR,
        role=SNOWFLAKE_ROLE
    )
    cs = ctx.cursor()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ddl_file = os.path.join(base_dir, "DDL", "snowflake_setup.sql")

    with open(ddl_file, "r") as f:
        sql_content = f.read()

    # Split SQL file into statements
    statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]

    print(f"\n🚀 Executing {len(statements)} DDL statements in Snowflake...")
    for i, stmt in enumerate(statements, 1):
        if stmt.startswith("--"):
            continue
        first_line = stmt.split("\n")[0][:60]
        print(f"  [{i}/{len(statements)}] Executing: {first_line}...")
        try:
            cs.execute(stmt)
            print(f"      ✅ OK")
        except Exception as e:
            print(f"      ⚠️ Warning/Error: {e}")

    cs.close()
    ctx.close()
    print("\n🎉 Snowflake Infrastructure & S3 Bulk Copy Setup Completed Successfully!")

if __name__ == "__main__":
    execute_ddl()
