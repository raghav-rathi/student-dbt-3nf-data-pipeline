{{ config(materialized='view') }}

SELECT
    TRIM(id) AS payor_id,
    TRIM(name) AS payor_name,
    TRIM(address) AS address,
    TRIM(city) AS city,
    TRIM(state) AS state,
    TRIM(zip) AS zip,
    TRIM(phone) AS phone
FROM {{ source('staging', 'raw_payors') }}
