{{ config(materialized='view') }}

SELECT
    TRIM(id) AS organization_id,
    TRIM(name) AS hospital_name,
    TRIM(address) AS address,
    TRIM(city) AS city,
    TRIM(state) AS state,
    TRIM(zip) AS zip,
    TRIM(phone) AS phone,
    CAST(revenue AS DECIMAL(12,2)) AS revenue
FROM {{ source('staging', 'raw_organizations') }}
