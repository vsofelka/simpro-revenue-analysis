with source as (
    select * from {{ source('hubspot', 'contacts') }}
),

cleaned as (
    select
        contact_id,
        first_name,
        last_name,
        email,
        company,
        lifecycle_stage,
        created_at
    from source
    where contact_id is not null
)

select * from cleaned
