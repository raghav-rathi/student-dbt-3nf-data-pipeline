{{ config(materialized='table') }}

WITH unnested AS (
    SELECT
        UNNEST(STRING_SPLIT(doctor_ids, ',')) AS doctor_id,
        UNNEST(STRING_SPLIT(doctor_names, ',')) AS doctor_name,
        UNNEST(STRING_SPLIT(doctor_specializations, ',')) AS specialization,
        UNNEST(STRING_SPLIT(department_ids, ',')) AS department_id
    FROM {{ ref('bronze_raw_hospital') }}
)
SELECT DISTINCT
    TRIM(doctor_id) AS doctor_id,
    TRIM(doctor_name) AS doctor_name,
    TRIM(specialization) AS specialization,
    TRIM(department_id) AS department_id
FROM unnested
WHERE doctor_id IS NOT NULL AND TRIM(doctor_id) != ''
