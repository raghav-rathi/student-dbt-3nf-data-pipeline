{{ config(materialized='view') }}

SELECT
    TRIM(id) AS patient_id,
    CAST(birthdate AS DATE) AS birth_date,
    CAST(deathdate AS DATE) AS death_date,
    TRIM(ssn) AS ssn,
    TRIM(first) AS first_name,
    TRIM(last) AS last_name,
    TRIM(gender) AS gender,
    TRIM(race) AS race,
    TRIM(ethnicity) AS ethnicity,
    TRIM(address) AS address,
    TRIM(city) AS city,
    TRIM(state) AS state,
    TRIM(zip) AS zip,
    TRIM(insurance_provider) AS insurance_provider,
    CAST(updated_at AS TIMESTAMP) AS updated_at
FROM {{ source('staging', 'raw_patients') }}
