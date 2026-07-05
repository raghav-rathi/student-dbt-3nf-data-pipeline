{{ config(materialized='table') }}

SELECT
    f.student_id,
    s.student_name,
    f.course_id,
    c.course_name,
    ci.instructor_id,
    i.instructor_name,
    i.instructor_dept,
    f.grade
FROM {{ ref('fact_enrollments') }} f
LEFT JOIN {{ ref('dim_students') }} s ON f.student_id = s.student_id
LEFT JOIN {{ ref('dim_courses') }} c ON f.course_id = c.course_id
LEFT JOIN {{ ref('course_instructors') }} ci ON f.course_id = ci.course_id
LEFT JOIN {{ ref('dim_instructors') }} i ON ci.instructor_id = i.instructor_id
