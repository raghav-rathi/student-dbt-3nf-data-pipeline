{{ config(materialized='table') }}

SELECT DISTINCT
    payor_id,
    payor_name,
    address,
    city,
    state,
    zip,
    phone
FROM {{ ref('stg_payors') }}
WHERE payor_id IS NOT NULL
