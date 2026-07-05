{{ config(materialized='table') }}

SELECT DISTINCT
    provider_id,
    organization_id,
    doctor_name,
    gender,
    speciality AS specialty,
    address,
    city,
    state,
    zip
FROM {{ ref('stg_providers') }}
WHERE provider_id IS NOT NULL
