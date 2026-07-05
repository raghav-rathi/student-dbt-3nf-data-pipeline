# 🔐 AWS S3 & Snowflake Credentials Setup Guide

This guide provides step-by-step instructions to set up your **AWS S3** bucket and **Snowflake Data Warehouse** credentials required for the automated Healthcare Data Pipeline.

---

## 📋 Credentials Checklist

By the end of this guide, you will have the following 9 configuration values ready for your `.env` file:

```env
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
AWS_REGION=us-east-1
S3_BUCKET_NAME=my-healthcare-pipeline-data

# Snowflake Configuration
SNOWFLAKE_ACCOUNT=xy12345.us-east-1  # or your Snowflake Organization-Account identifier
SNOWFLAKE_USER=MY_SNOWFLAKE_USER
SNOWFLAKE_PASSWORD=MySecurePassword123!
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=HEALTHCARE_DB
SNOWFLAKE_ROLE=ACCOUNTADMIN           # or SYSADMIN
```

---

## ☁️ PART 1: AWS Setup (S3 Bucket & IAM Access Keys)

### Step 1: Create an S3 Bucket
1. Log in to the [AWS Management Console](https://console.aws.amazon.com/).
2. Navigate to **S3** → Click **Create bucket**.
3. Set **Bucket Name**: e.g., `healthcare-pipeline-data-yourname` (must be globally unique).
4. Set **AWS Region**: Select your closest region (e.g. `us-east-1` N. Virginia).
5. Leave all default settings (*Block all public access* enabled) and click **Create bucket**.

---

### Step 2: Create IAM Access Keys for Automation
1. In the AWS Console search bar, search for **IAM** (Identity and Access Management).
2. Click **Users** in the left sidebar → Click **Create user**.
3. Set **User name**: `dbt-snowflake-pipeline-user` → Click **Next**.
4. Set Permissions:
   - Select **Attach policies directly**.
   - Search for `AmazonS3FullAccess` → Check the checkbox.
   - Click **Next** → Click **Create user**.
5. Click on the newly created user `dbt-snowflake-pipeline-user`.
6. Go to the **Security credentials** tab → Scroll down to **Access keys** → Click **Create access key**.
7. Choose **Command Line Interface (CLI)** → Check the acknowledgment checkbox → Click **Next**.
8. Click **Create access key**.
9. ⚠️ **Copy both keys immediately**:
   - `AWS_ACCESS_KEY_ID` (starts with `AKIA...`)
   - `AWS_SECRET_ACCESS_KEY` (long secret string)

---

## ❄️ PART 2: Snowflake Account Setup

If you don't have a Snowflake account, sign up for a **30-Day Free Trial ($400 Free Credits)** at [signup.snowflake.com](https://signup.snowflake.com/) (select Enterprise Edition on AWS).

### Step 1: Find Your Snowflake Account Identifier
1. Log in to your Snowflake Web UI (Snowsight).
2. Look at your browser URL or click on your account name in the bottom-left corner.
3. Your **Account Identifier** format:
   - Format: `<orgname>-<accountname>` or `<account_locator>.<region>`
   - Example 1: `xy12345.us-east-1`
   - Example 2: `myorg-myaccount`
   *(Do NOT include `https://` or `.snowflakecomputing.com` in your account variable).*

---

### Step 2: Create Warehouse, Database & Schema (SQL Script)
1. In Snowflake, open a new **SQL Worksheet**.
2. Run the following setup script to create your database, staging schema, and warehouse:

```sql
-- 1. Create Warehouse
CREATE WAREHOUSE IF NOT EXISTS COMPUTE_WH
  WITH WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;

-- 2. Create Database
CREATE DATABASE IF NOT EXISTS HEALTHCARE_DB;

-- 3. Create Staging Schema for Raw S3 Data
CREATE SCHEMA IF NOT EXISTS HEALTHCARE_DB.STAGING;

-- 4. Create Bronze, Silver, Gold Schemas for dbt
CREATE SCHEMA IF NOT EXISTS HEALTHCARE_DB.BRONZE;
CREATE SCHEMA IF NOT EXISTS HEALTHCARE_DB.SILVER;
CREATE SCHEMA IF NOT EXISTS HEALTHCARE_DB.GOLD;

-- 5. Verify Setup
USE WAREHOUSE COMPUTE_WH;
USE DATABASE HEALTHCARE_DB;
SHOW SCHEMAS;
```

---

## 📄 PART 3: Saving Credentials to `.env`

Create a file named `.env` in the root directory of your project and paste your completed values:

```bash
# Save to: /Users/whiterose/.gemini/antigravity-ide/scratch/HarshProject/.env

AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket-name

SNOWFLAKE_ACCOUNT=your-account-id
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=HEALTHCARE_DB
SNOWFLAKE_ROLE=ACCOUNTADMIN
```

---

## 🚀 How These Credentials Will Be Used

Once you provide these credential variables:
1. **Automated S3 Sync**: Python uploads all Synthea CSV files directly to `s3://S3_BUCKET_NAME/raw/`.
2. **Snowflake DDL Execution**: Python connects to Snowflake, creates the S3 Stage, and executes `COPY INTO HEALTHCARE_DB.STAGING.*`.
3. **dbt Medallion Pipeline**: dbt connects to Snowflake using `profiles.yml` and builds Bronze views, Silver 3NF tables, SCD Type 2 Snapshots, and Gold Star Schema models.
