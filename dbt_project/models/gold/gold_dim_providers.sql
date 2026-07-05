{{ config(materialized='table') }}

WITH provider_stats AS (
    SELECT
        provider_id,
        COUNT(DISTINCT patient_id) AS total_patients_seen,
        COUNT(encounter_id) AS total_encounters_handled,
        SUM(total_claim_cost) AS total_revenue_generated
    FROM {{ ref('fct_encounters') }}
    GROUP BY provider_id
)

SELECT
    d.provider_id,
    d.doctor_name,
    d.gender,
    d.specialty,
    o.hospital_name,
    o.city AS hospital_city,
    COALESCE(s.total_patients_seen, 0) AS total_patients_seen,
    COALESCE(s.total_encounters_handled, 0) AS total_encounters_handled,
    COALESCE(ROUND(s.total_revenue_generated, 2), 0.00) AS total_revenue_generated
FROM {{ ref('dim_providers') }} d
LEFT JOIN {{ ref('dim_organizations') }} o ON d.organization_id = o.organization_id
LEFT JOIN provider_stats s ON d.provider_id = s.provider_id
