{{ config(materialized='table') }}

WITH unnested AS (
    SELECT
        UNNEST(STRING_SPLIT(CourseIDs, ',')) AS course_id,
        UNNEST(STRING_SPLIT(InstructorID, ',')) AS instructor_id
    FROM {{ ref('bronze_raw_students') }}
)
SELECT DISTINCT
    TRIM(course_id) AS course_id,
    TRIM(instructor_id) AS instructor_id
FROM unnested
WHERE course_id IS NOT NULL AND TRIM(course_id) != ''
  AND instructor_id IS NOT NULL AND TRIM(instructor_id) != ''
