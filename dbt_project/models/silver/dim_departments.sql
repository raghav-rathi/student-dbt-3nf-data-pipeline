{{ config(materialized='table') }}

WITH unnested AS (
    SELECT
        UNNEST(STRING_SPLIT(department_ids, ',')) AS department_id,
        UNNEST(STRING_SPLIT(department_names, ',')) AS department_name
    FROM {{ ref('bronze_raw_hospital') }}
)
SELECT DISTINCT
    TRIM(department_id) AS department_id,
    TRIM(department_name) AS department_name
FROM unnested
WHERE department_id IS NOT NULL AND TRIM(department_id) != ''
