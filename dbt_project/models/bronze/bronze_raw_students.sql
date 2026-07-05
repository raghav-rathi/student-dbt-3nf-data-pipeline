{{ config(materialized='table') }}

SELECT
    TRIM(StudentID) AS StudentID,
    TRIM(StudentName) AS StudentName,
    TRIM(StudentPhone) AS StudentPhone,
    TRIM(CourseIDs) AS CourseIDs,
    TRIM(CourseNames) AS CourseNames,
    TRIM(InstructorID) AS InstructorID,
    TRIM(InstructorName) AS InstructorName,
    TRIM(InstructorDept) AS InstructorDept,
    TRIM(Grade) AS Grade
FROM read_csv_auto('/Users/whiterose/.gemini/antigravity-ide/scratch/HarshProject/data/raw_student_courses.csv')
