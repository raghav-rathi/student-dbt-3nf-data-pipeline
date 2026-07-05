{{ config(materialized='table') }}

WITH unnested AS (
    SELECT
        UNNEST(STRING_SPLIT(medication_ids, ',')) AS medication_id,
        UNNEST(STRING_SPLIT(medication_names, ',')) AS medication_name
    FROM {{ ref('bronze_raw_hospital') }}
)
SELECT DISTINCT
    TRIM(medication_id) AS medication_id,
    TRIM(medication_name) AS medication_name
FROM unnested
WHERE medication_id IS NOT NULL AND TRIM(medication_id) != ''
