{{ config(materialized='table') }}

WITH unnested AS (
    SELECT
        TRIM(StudentID) AS student_id,
        UNNEST(STRING_SPLIT(CourseIDs, ',')) AS course_id,
        UNNEST(STRING_SPLIT(Grade, ',')) AS grade
    FROM {{ ref('bronze_raw_students') }}
)
SELECT DISTINCT
    student_id,
    TRIM(course_id) AS course_id,
    TRIM(grade) AS grade
FROM unnested
WHERE student_id IS NOT NULL AND course_id IS NOT NULL
