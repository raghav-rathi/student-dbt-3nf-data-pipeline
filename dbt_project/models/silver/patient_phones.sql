{{ config(materialized='table') }}

WITH split_phones AS (
    SELECT
        TRIM(patient_id) AS patient_id,
        UNNEST(STRING_SPLIT(patient_phone, ',')) AS phone_number
    FROM {{ ref('bronze_raw_hospital') }}
)
SELECT DISTINCT
    patient_id,
    TRIM(phone_number) AS phone_number
FROM split_phones
WHERE phone_number IS NOT NULL AND TRIM(phone_number) != ''
