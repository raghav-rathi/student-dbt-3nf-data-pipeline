{{ config(materialized='table') }}

SELECT
    patient_id,
    encounter_id,
    medication_code,
    medication_description,
    start_time,
    stop_time,
    base_cost,
    payer_coverage,
    dispenses,
    total_cost,
    ROUND(total_cost - payer_coverage, 2) AS patient_out_of_pocket
FROM {{ ref('stg_medications') }}
WHERE patient_id IS NOT NULL AND encounter_id IS NOT NULL
