{{ config(materialized='table') }}

SELECT DISTINCT
    patient_id,
    first_name,
    last_name,
    gender,
    birth_date,
    death_date,
    ssn,
    race,
    ethnicity,
    address,
    city,
    state,
    zip,
    insurance_provider
FROM {{ ref('stg_patients') }}
WHERE patient_id IS NOT NULL
