{{ config(materialized='view') }}

SELECT
    TRIM(id) AS encounter_id,
    CAST("start" AS TIMESTAMP) AS start_time,
    CAST("stop" AS TIMESTAMP) AS stop_time,
    TRIM(patient) AS patient_id,
    TRIM(organization) AS organization_id,
    TRIM(provider) AS provider_id,
    TRIM(payor) AS payor_id,
    TRIM(encounterclass) AS encounter_class,
    CAST(code AS VARCHAR) AS encounter_code,
    TRIM(description) AS encounter_description,
    CAST(base_encounter_cost AS DECIMAL(12,2)) AS base_encounter_cost,
    CAST(total_claim_cost AS DECIMAL(12,2)) AS total_claim_cost,
    CAST(payer_coverage AS DECIMAL(12,2)) AS payer_coverage,
    CAST(reasoncode AS VARCHAR) AS reason_code,
    TRIM(reasondescription) AS reason_description
FROM {{ source('staging', 'RAW_ENCOUNTERS') }}
