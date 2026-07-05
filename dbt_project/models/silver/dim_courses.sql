{{ config(materialized='table') }}

WITH unnested AS (
    SELECT
        UNNEST(STRING_SPLIT(CourseIDs, ',')) AS course_id,
        UNNEST(STRING_SPLIT(CourseNames, ',')) AS course_name
    FROM {{ ref('bronze_raw_students') }}
)
SELECT DISTINCT
    TRIM(course_id) AS course_id,
    TRIM(course_name) AS course_name
FROM unnested
WHERE course_id IS NOT NULL AND TRIM(course_id) != ''
