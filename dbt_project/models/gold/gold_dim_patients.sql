{{ config(materialized='table') }}

WITH encounter_stats AS (
    SELECT
        patient_id,
        COUNT(encounter_id) AS total_encounters,
        SUM(total_claim_cost) AS lifetime_claim_cost,
        SUM(patient_out_of_pocket_cost) AS lifetime_out_of_pocket,
        AVG(length_of_stay_hours) AS avg_length_of_stay_hours
    FROM {{ ref('fct_encounters') }}
    GROUP BY patient_id
)

SELECT
    p.patient_id,
    p.first_name,
    p.last_name,
    p.gender,
    p.birth_date,
    p.race,
    p.ethnicity,
    p.address,
    p.city,
    p.state,
    p.zip,
    p.insurance_provider,
    COALESCE(s.total_encounters, 0) AS total_encounters,
    COALESCE(ROUND(s.lifetime_claim_cost, 2), 0.00) AS lifetime_claim_cost,
    COALESCE(ROUND(s.lifetime_out_of_pocket, 2), 0.00) AS lifetime_out_of_pocket,
    COALESCE(ROUND(s.avg_length_of_stay_hours, 1), 0.0) AS avg_length_of_stay_hours
FROM {{ ref('dim_patients') }} p
LEFT JOIN encounter_stats s ON p.patient_id = s.patient_id
