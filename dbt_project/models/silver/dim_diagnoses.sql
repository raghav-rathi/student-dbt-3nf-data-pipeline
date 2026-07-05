{{ config(materialized='table') }}

WITH unnested AS (
    SELECT
        UNNEST(STRING_SPLIT(diagnosis_codes, ',')) AS diagnosis_code,
        UNNEST(STRING_SPLIT(diagnosis_descriptions, ',')) AS diagnosis_description
    FROM {{ ref('bronze_raw_hospital') }}
)
SELECT DISTINCT
    TRIM(diagnosis_code) AS diagnosis_code,
    TRIM(diagnosis_description) AS diagnosis_description
FROM unnested
WHERE diagnosis_code IS NOT NULL AND TRIM(diagnosis_code) != ''
