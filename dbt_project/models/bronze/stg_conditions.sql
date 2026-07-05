{{ config(materialized='view') }}

SELECT
    CAST("start" AS DATE) AS onset_date,
    CAST("stop" AS DATE) AS resolution_date,
    TRIM(patient) AS patient_id,
    TRIM(encounter) AS encounter_id,
    CAST(code AS VARCHAR) AS condition_code,
    TRIM(description) AS condition_description
FROM {{ source('staging', 'RAW_CONDITIONS') }}
