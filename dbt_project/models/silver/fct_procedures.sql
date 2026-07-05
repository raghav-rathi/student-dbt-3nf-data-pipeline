{{ config(materialized='table') }}

SELECT
    patient_id,
    encounter_id,
    procedure_code,
    procedure_description,
    start_time,
    stop_time,
    base_cost
FROM {{ ref('stg_procedures') }}
WHERE patient_id IS NOT NULL AND encounter_id IS NOT NULL
