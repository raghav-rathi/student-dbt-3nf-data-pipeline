{% snapshot snapshot_patients %}

{{
    config(
      target_schema='snapshots',
      unique_key='patient_id',
      strategy='timestamp',
      updated_at='updated_at'
    )
}}

SELECT
    TRIM(id) AS patient_id,
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
FROM {{ source('staging', 'RAW_PATIENTS') }}

{% endsnapshot %}
