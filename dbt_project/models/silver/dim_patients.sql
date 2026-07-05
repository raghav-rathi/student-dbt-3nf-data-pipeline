{{ config(materialized='table') }}

SELECT DISTINCT
    TRIM(patient_id) AS patient_id,
    TRIM(patient_name) AS patient_name,
    CAST(patient_dob AS DATE) AS patient_dob,
    TRIM(patient_gender) AS patient_gender
FROM {{ ref('bronze_raw_hospital') }}
WHERE patient_id IS NOT NULL
