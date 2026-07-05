{{ config(materialized='table') }}

SELECT
    v.patient_id,
    p.patient_name,
    p.patient_gender,
    p.patient_dob,
    v.visit_date,
    v.visit_type,
    v.billing_amount,
    pd.doctor_id,
    d.doctor_name,
    d.specialization,
    dept.department_id,
    dept.department_name,
    pdiag.diagnosis_code,
    diag.diagnosis_description,
    pm.medication_id,
    med.medication_name,
    pm.dosage
FROM {{ ref('fact_visits') }} v
LEFT JOIN {{ ref('dim_patients') }} p ON v.patient_id = p.patient_id
LEFT JOIN {{ ref('patient_doctors') }} pd ON v.patient_id = pd.patient_id
LEFT JOIN {{ ref('dim_doctors') }} d ON pd.doctor_id = d.doctor_id
LEFT JOIN {{ ref('dim_departments') }} dept ON d.department_id = dept.department_id
LEFT JOIN {{ ref('patient_diagnoses') }} pdiag ON v.patient_id = pdiag.patient_id
LEFT JOIN {{ ref('dim_diagnoses') }} diag ON pdiag.diagnosis_code = diag.diagnosis_code
LEFT JOIN {{ ref('patient_medications') }} pm ON v.patient_id = pm.patient_id
LEFT JOIN {{ ref('dim_medications') }} med ON pm.medication_id = med.medication_id
