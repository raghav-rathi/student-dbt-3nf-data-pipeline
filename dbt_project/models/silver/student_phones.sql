{{ config(materialized='table') }}

WITH split_phones AS (
    SELECT
        TRIM(StudentID) AS student_id,
        UNNEST(STRING_SPLIT(StudentPhone, ',')) AS phone_number
    FROM {{ ref('bronze_raw_students') }}
)
SELECT DISTINCT
    student_id,
    TRIM(phone_number) AS phone_number
FROM split_phones
WHERE phone_number IS NOT NULL AND TRIM(phone_number) != ''
