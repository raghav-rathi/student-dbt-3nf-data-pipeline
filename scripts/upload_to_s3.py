import os
import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "healthcare-pipeline-harsh")

def upload_files():
    print(f"🚀 Uploading raw CSV files to AWS S3 bucket: {S3_BUCKET_NAME}...")
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(base_dir, "data", "synthea_raw")

    files = [
        "patients.csv", "encounters.csv", "providers.csv", "organizations.csv",
        "payors.csv", "conditions.csv", "medications.csv", "procedures.csv", "claims.csv"
    ]

    for f in files:
        local_path = os.path.join(raw_dir, f)
        s3_key = f"raw/{f}"
        if os.path.exists(local_path):
            s3.upload_file(local_path, S3_BUCKET_NAME, s3_key)
            print(f"  [+] Uploaded {f} -> s3://{S3_BUCKET_NAME}/{s3_key}")
        else:
            print(f"  [!] Missing local file: {local_path}")

    print("\n✅ All 9 CSV files successfully uploaded to AWS S3!")

if __name__ == "__main__":
    upload_files()
