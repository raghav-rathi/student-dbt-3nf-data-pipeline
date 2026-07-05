{{ config(materialized='table') }}

SELECT
    TRIM(PatientID) AS patient_id,
    TRIM(PatientName) AS patient_name,
    TRIM(PatientPhone) AS patient_phone,
    CAST(PatientDOB AS VARCHAR) AS patient_dob,
    TRIM(PatientGender) AS patient_gender,
    TRIM(DoctorIDs) AS doctor_ids,
    TRIM(DoctorNames) AS doctor_names,
    TRIM(DoctorSpecializations) AS doctor_specializations,
    TRIM(DepartmentIDs) AS department_ids,
    TRIM(DepartmentNames) AS department_names,
    TRIM(DiagnosisCodes) AS diagnosis_codes,
    TRIM(DiagnosisDescriptions) AS diagnosis_descriptions,
    TRIM(MedicationIDs) AS medication_ids,
    TRIM(MedicationNames) AS medication_names,
    TRIM(MedicationDosages) AS medication_dosages,
    TRIM(VisitDates) AS visit_dates,
    TRIM(VisitTypes) AS visit_types,
    TRIM(BillingAmounts) AS billing_amounts
FROM read_csv_auto(
    '../data/raw_hospital_records.csv',
    header=true
)
