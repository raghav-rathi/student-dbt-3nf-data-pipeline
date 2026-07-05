{{ config(materialized='table') }}

WITH unnested AS (
    SELECT
        TRIM(patient_id) AS patient_id,
        UNNEST(STRING_SPLIT(diagnosis_codes, ',')) AS diagnosis_code
    FROM {{ ref('bronze_raw_hospital') }}
)
SELECT DISTINCT
    patient_id,
    TRIM(diagnosis_code) AS diagnosis_code
FROM unnested
WHERE patient_id IS NOT NULL AND diagnosis_code IS NOT NULL AND TRIM(diagnosis_code) != ''
