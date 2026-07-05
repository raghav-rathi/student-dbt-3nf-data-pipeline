{{ config(materialized='table') }}

SELECT DISTINCT
    TRIM(StudentID) AS student_id,
    TRIM(StudentName) AS student_name
FROM {{ ref('bronze_raw_students') }}
WHERE StudentID IS NOT NULL
