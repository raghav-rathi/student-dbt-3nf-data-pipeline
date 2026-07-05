{{ config(materialized='table') }}

WITH unnested AS (
    SELECT
        TRIM(patient_id) AS patient_id,
        UNNEST(STRING_SPLIT(doctor_ids, ',')) AS doctor_id
    FROM {{ ref('bronze_raw_hospital') }}
)
SELECT DISTINCT
    patient_id,
    TRIM(doctor_id) AS doctor_id
FROM unnested
WHERE patient_id IS NOT NULL AND doctor_id IS NOT NULL AND TRIM(doctor_id) != ''
