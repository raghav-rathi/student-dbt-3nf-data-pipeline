{{ config(materialized='view') }}

SELECT
    TRIM(id) AS provider_id,
    TRIM(organization) AS organization_id,
    TRIM(name) AS doctor_name,
    TRIM(gender) AS gender,
    TRIM(speciality) AS speciality,
    TRIM(address) AS address,
    TRIM(city) AS city,
    TRIM(state) AS state,
    TRIM(zip) AS zip
FROM {{ source('staging', 'raw_providers') }}
