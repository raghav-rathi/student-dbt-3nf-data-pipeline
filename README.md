# 🎓 Student DBT 3NF Data Pipeline

## 📋 Executive Summary
This project takes an unnormalized student enrollment dataset containing multi-valued attributes and normalizes it up to **3rd Normal Form (3NF)** using **DBT (Data Build Tool)** and **DuckDB**. It outputs an analytics-ready Star Schema table for **Power BI reporting**.

---

## 🏗️ Architecture & Medallion Layers

```text
raw_student_courses.csv (Raw Ingestion)
          │
          ▼
  🥉 BRONZE LAYER (`bronze_raw_students`)
          │
          ▼ (3NF Normalization: String Splitting & Unnesting)
  🥈 SILVER LAYER (Normalized 3NF Tables)
    ├── dim_students
    ├── student_phones
    ├── dim_courses
    ├── dim_instructors
    ├── course_instructors
    └── fact_enrollments
          │
          ▼ (Star Schema Join & Denormalization)
  🥇 GOLD LAYER (`obt_student_analytics`) -> Exported to Power BI
```

---

## 📐 3NF Normalization Proofs

### 1. First Normal Form (1NF)
- **Violation in Raw:** `StudentPhone`, `CourseIDs`, `CourseNames`, `InstructorID`, `InstructorName`, `InstructorDept`, and `Grade` contained comma-separated multi-valued lists (e.g. `98765, 98764`).
- **1NF Solution:** All repeating attributes were unnested using DuckDB's `UNNEST(STRING_SPLIT(...))` into individual atomic rows.

### 2. Second Normal Form (2NF)
- **Violation in Raw:** Course details (`CourseNames`) depended only on `CourseIDs`, and Instructor details (`InstructorName`, `InstructorDept`) depended only on `InstructorID`, creating partial key dependencies.
- **2NF Solution:** Extracted `dim_courses` and `dim_instructors` so non-key attributes depend on their entire candidate primary key.

### 3. Third Normal Form (3NF)
- **Violation in Raw:** Transitive dependencies existed where `InstructorDept` depended on `InstructorID`, not `StudentID`.
- **3NF Solution:** Separated into 6 atomic entities:
  1. `dim_students` (`student_id` [PK], `student_name`)
  2. `student_phones` (`student_id` [FK], `phone_number`)
  3. `dim_courses` (`course_id` [PK], `course_name`)
  4. `dim_instructors` (`instructor_id` [PK], `instructor_name`, `instructor_dept`)
  5. `course_instructors` (`course_id` [FK], `instructor_id` [FK])
  6. `fact_enrollments` (`student_id` [FK], `course_id` [FK], `grade`)

---

## 📊 Summary of Data Warehouse Tables

### 1. `dim_students`
| student_id | student_name |
| :--- | :--- |
| S01 | Rahul Sharma |
| S02 | Priya Mehta |
| S03 | Amit Verma |

### 2. `student_phones`
| student_id | phone_number |
| :--- | :--- |
| S01 | 98765 |
| S01 | 98764 |
| S02 | 91234 |
| S03 | 99887 |
| S03 | 99886 |

### 3. `dim_courses`
| course_id | course_name |
| :--- | :--- |
| C01 | Java |
| C02 | DBMS |
| C03 | Networks |

### 4. `dim_instructors`
| instructor_id | instructor_name | instructor_dept |
| :--- | :--- | :--- |
| I10 | Anil Kumar | Computer Science |
| I11 | Sneha Rao | Information Tech |
| I12 | Vikram Das | Computer Science |

### 5. `fact_enrollments`
| student_id | course_id | grade |
| :--- | :--- | :--- |
| S01 | C01 | A |
| S01 | C02 | B |
| S02 | C01 | A |
| S03 | C02 | C |
| S03 | C03 | B |

---

## 🚀 Execution Instructions

```bash
# 1. Activate Virtual Environment
source venv/bin/activate

# 2. Run DBT Pipeline
cd dbt_project
dbt run

# 3. Execute Data Quality Tests
dbt test
```

---

## 📦 Deliverables Checklist
- [x] **DBT Project (ZIP):** `student_dbt_3nf_data_pipeline.zip`
- [x] **Data Warehouse Screenshots/Outputs:** `screenshots/data_warehouse_tables.txt`
- [x] **Power BI Dataset:** `power_bi/obt_student_analytics.csv`
- [x] **Power BI Setup Guide:** `power_bi/power_bi_setup_guide.md`
