{{ config(materialized='table') }}

SELECT
    fe.encounter_id,
    fe.encounter_start_at,
    fe.encounter_stop_at,
    fe.encounter_class,
    fe.encounter_description,
    fe.length_of_stay_hours,
    fe.total_claim_cost,
    fe.payer_coverage,
    fe.patient_out_of_pocket_cost,
    
    -- Patient Details
    dp.patient_id,
    dp.first_name AS patient_first_name,
    dp.last_name AS patient_last_name,
    dp.gender AS patient_gender,
    dp.race AS patient_race,
    dp.birth_date AS patient_birth_date,
    dp.insurance_provider AS patient_insurance,
    
    -- Doctor Details
    dprov.provider_id,
    dprov.doctor_name,
    dprov.specialty AS doctor_specialty,
    
    -- Hospital Details
    dorg.organization_id,
    dorg.hospital_name,
    dorg.city AS hospital_city,
    dorg.state AS hospital_state,
    
    -- Payor Details
    dpay.payor_id,
    dpay.payor_name,
    
    -- Condition & Medication details (sample aggregate)
    c.condition_description,
    m.medication_description
FROM {{ ref('fct_encounters') }} fe
LEFT JOIN {{ ref('dim_patients') }} dp ON fe.patient_id = dp.patient_id
LEFT JOIN {{ ref('dim_providers') }} dprov ON fe.provider_id = dprov.provider_id
LEFT JOIN {{ ref('dim_organizations') }} dorg ON fe.organization_id = dorg.organization_id
LEFT JOIN {{ ref('dim_payors') }} dpay ON fe.payor_id = dpay.payor_id
LEFT JOIN {{ ref('fct_conditions') }} c ON fe.encounter_id = c.encounter_id
LEFT JOIN {{ ref('fct_medications') }} m ON fe.encounter_id = m.encounter_id
