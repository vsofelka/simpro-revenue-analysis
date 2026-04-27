with source as (
    select * from {{ source('hubspot', 'stages') }}
),

cleaned as (
    select
        stage_id,
        stage_name,
        pipeline_id,
        display_order,
        win_probability
    from source
    where stage_id is not null
)

select * from cleaned
