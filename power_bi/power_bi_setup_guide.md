# Power BI Report (.PBIX) Setup Guide

This guide explains how to import your generated Gold Star Schema dataset into **Power BI Desktop** and build the required report to submit as **`report.pbix`**.

---

## Step 1: Import Dataset into Power BI Desktop
1. Open **Power BI Desktop**.
2. Click **Get Data** -> **Text/CSV**.
3. Browse to your project folder and select:
   `HarshProject/power_bi/obt_student_analytics.csv`
4. Click **Load**.

---

## Step 2: Build Visualizations

Create the following 4 visuals on your Power BI Report Canvas:

### Visual 1: Summary KPI Cards (Top Header)
- **Card 1:** Total Students -> Field: `student_id` (Count Distinct) -> Output: `3`
- **Card 2:** Total Courses -> Field: `course_id` (Count Distinct) -> Output: `3`
- **Card 3:** Total Instructors -> Field: `instructor_id` (Count Distinct) -> Output: `3`
- **Card 4:** Total Enrollments -> Field: `student_id` (Count) -> Output: `5`

### Visual 2: Grade Distribution (Clustered Bar Chart)
- **Axis (Y-Axis):** `grade`
- **Values (X-Axis):** `student_id` (Count)
- **Title:** *Student Grade Distribution*

### Visual 3: Course Enrollments by Department (Donut / Pie Chart)
- **Legend:** `instructor_dept`
- **Values:** `course_id` (Count)
- **Title:** *Enrollments by Department*

### Visual 4: Master Student Enrollment Detail (Table Visual)
- Add Columns: `student_id`, `student_name`, `course_name`, `instructor_name`, `instructor_dept`, `grade`
- **Title:** *Student Enrollment Matrix*

---

## Step 3: Save & Submit
1. Click **File** -> **Save As**.
2. Save the file as **`student_analytics_report.pbix`** inside the `power_bi/` directory.
3. Submit this `.pbix` file along with the `HarshProject_DBT.zip`!
