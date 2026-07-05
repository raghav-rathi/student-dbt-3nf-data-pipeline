{{ config(materialized='table') }}

WITH unnested AS (
    SELECT
        TRIM(patient_id) AS patient_id,
        UNNEST(STRING_SPLIT(visit_dates, ',')) AS visit_date,
        UNNEST(STRING_SPLIT(visit_types, ',')) AS visit_type,
        UNNEST(STRING_SPLIT(billing_amounts, ',')) AS billing_amount
    FROM {{ ref('bronze_raw_hospital') }}
)
SELECT DISTINCT
    patient_id,
    CAST(TRIM(visit_date) AS DATE) AS visit_date,
    TRIM(visit_type) AS visit_type,
    CAST(TRIM(billing_amount) AS DECIMAL(10,2)) AS billing_amount
FROM unnested
WHERE patient_id IS NOT NULL AND TRIM(visit_date) != ''
