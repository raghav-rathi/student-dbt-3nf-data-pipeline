{{ config(materialized='table') }}

SELECT
    claim_id,
    patient_id,
    provider_id,
    claim_status,
    outstanding_date,
    service_date
FROM {{ ref('stg_claims') }}
WHERE claim_id IS NOT NULL
