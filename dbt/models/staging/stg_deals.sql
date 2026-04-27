with source as (
    select * from {{ source('hubspot', 'deals') }}
),

cleaned as (
    select
        deal_id,
        deal_name,
        coalesce(amount, 0)  as amount,
        deal_stage,
        pipeline_id,
        close_date,
        created_at,
        primary_contact_id
    from source
    where deal_id is not null
)

select * from cleaned
