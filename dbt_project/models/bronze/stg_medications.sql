{{ config(materialized='view') }}

SELECT
    CAST(start AS TIMESTAMP) AS start_time,
    CAST(stop AS TIMESTAMP) AS stop_time,
    TRIM(patient) AS patient_id,
    TRIM(encounter) AS encounter_id,
    CAST(code AS VARCHAR) AS medication_code,
    TRIM(description) AS medication_description,
    CAST(base_cost AS DECIMAL(12,2)) AS base_cost,
    CAST(payer_coverage AS DECIMAL(12,2)) AS payer_coverage,
    CAST(dispenses AS INT) AS dispenses,
    CAST(totalcost AS DECIMAL(12,2)) AS total_cost
FROM {{ source('staging', 'raw_medications') }}
