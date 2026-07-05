{{ config(materialized='view') }}

SELECT
    CAST("start" AS TIMESTAMP) AS start_time,
    CAST("stop" AS TIMESTAMP) AS stop_time,
    TRIM(patient) AS patient_id,
    TRIM(encounter) AS encounter_id,
    CAST(code AS VARCHAR) AS procedure_code,
    TRIM(description) AS procedure_description,
    CAST(base_cost AS DECIMAL(12,2)) AS base_cost
FROM {{ source('staging', 'RAW_PROCEDURES') }}
