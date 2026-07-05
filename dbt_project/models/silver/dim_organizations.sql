{{ config(materialized='table') }}

SELECT DISTINCT
    organization_id,
    hospital_name,
    address,
    city,
    state,
    zip,
    phone,
    revenue
FROM {{ ref('stg_organizations') }}
WHERE organization_id IS NOT NULL
