{{ config(materialized='view') }}

SELECT
    TRIM(id) AS claim_id,
    TRIM(patient) AS patient_id,
    TRIM(provider) AS provider_id,
    TRIM(status) AS claim_status,
    CAST(outstandingdate AS DATE) AS outstanding_date,
    CAST(servicedate AS DATE) AS service_date
FROM {{ source('staging', 'raw_claims') }}
