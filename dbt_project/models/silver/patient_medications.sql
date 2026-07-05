{{ config(materialized='table') }}

WITH unnested AS (
    SELECT
        TRIM(patient_id) AS patient_id,
        UNNEST(STRING_SPLIT(medication_ids, ',')) AS medication_id,
        UNNEST(STRING_SPLIT(medication_dosages, ',')) AS dosage
    FROM {{ ref('bronze_raw_hospital') }}
)
SELECT DISTINCT
    patient_id,
    TRIM(medication_id) AS medication_id,
    TRIM(dosage) AS dosage
FROM unnested
WHERE patient_id IS NOT NULL AND medication_id IS NOT NULL AND TRIM(medication_id) != ''
