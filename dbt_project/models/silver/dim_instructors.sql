{{ config(materialized='table') }}

WITH unnested AS (
    SELECT
        UNNEST(STRING_SPLIT(InstructorID, ',')) AS instructor_id,
        UNNEST(STRING_SPLIT(InstructorName, ',')) AS instructor_name,
        UNNEST(STRING_SPLIT(InstructorDept, ',')) AS instructor_dept
    FROM {{ ref('bronze_raw_students') }}
)
SELECT DISTINCT
    TRIM(instructor_id) AS instructor_id,
    TRIM(instructor_name) AS instructor_name,
    TRIM(instructor_dept) AS instructor_dept
FROM unnested
WHERE instructor_id IS NOT NULL AND TRIM(instructor_id) != ''
