{{ config(materialized='table') }}

SELECT
    e.encounter_id,
    e.encounter_start_at,
    e.encounter_stop_at,
    e.encounter_class,
    e.encounter_description,
    
    -- Foreign Keys
    e.patient_id,
    e.provider_id,
    e.organization_id,
    e.payor_id,
    
    -- Demographics at Encounter
    p.gender AS patient_gender,
    p.race AS patient_race,
    p.insurance_provider AS insurance_at_visit,
    
    -- Provider & Facility
    d.doctor_name,
    d.specialty AS doctor_specialty,
    o.hospital_name,
    py.payor_name,
    
    -- Financial Measures
    e.base_encounter_cost,
    e.total_claim_cost,
    e.payer_coverage,
    e.patient_out_of_pocket_cost,
    e.length_of_stay_hours
FROM {{ ref('fct_encounters') }} e
LEFT JOIN {{ ref('dim_patients') }} p ON e.patient_id = p.patient_id
LEFT JOIN {{ ref('dim_providers') }} d ON e.provider_id = d.provider_id
LEFT JOIN {{ ref('dim_organizations') }} o ON e.organization_id = o.organization_id
LEFT JOIN {{ ref('dim_payors') }} py ON e.payor_id = py.payor_id
