{{ config(materialized='table') }}

SELECT
    patient_id,
    encounter_id,
    condition_code,
    condition_description,
    onset_date,
    resolution_date
FROM {{ ref('stg_conditions') }}
WHERE patient_id IS NOT NULL AND encounter_id IS NOT NULL
