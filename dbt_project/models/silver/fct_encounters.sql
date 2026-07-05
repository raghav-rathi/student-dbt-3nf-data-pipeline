{{ config(
    materialized='incremental',
    unique_key='encounter_id'
) }}

WITH source_encounters AS (
    SELECT * FROM {{ ref('stg_encounters') }}
),

transformed AS (
    SELECT
        encounter_id,
        patient_id,
        provider_id,
        organization_id,
        payor_id,
        encounter_class,
        encounter_code,
        encounter_description,
        start_time AS encounter_start_at,
        stop_time AS encounter_stop_at,
        
        -- Business transformation 1: Length of stay in hours
        CAST(
            CASE 
                WHEN stop_time IS NOT NULL AND start_time IS NOT NULL 
                THEN date_diff('hour', start_time, stop_time)
                ELSE 0 
            END AS INT
        ) AS length_of_stay_hours,

        -- Business transformation 2: Financial metrics
        base_encounter_cost,
        total_claim_cost,
        payer_coverage,
        ROUND(total_claim_cost - payer_coverage, 2) AS patient_out_of_pocket_cost,
        
        reason_code,
        reason_description
    FROM source_encounters
)

SELECT * FROM transformed

{% if is_incremental() %}
  -- Filter for incremental execution
  WHERE encounter_start_at >= (
      SELECT COALESCE(MAX(encounter_start_at), CAST('1970-01-01' AS TIMESTAMP)) FROM {{ this }}
  )
{% endif %}
