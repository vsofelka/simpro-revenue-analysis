with stages as (
    select * from {{ ref('stg_pipeline_stages') }}
)

select
    stage_id,
    stage_name,
    pipeline_id,
    display_order,
    win_probability
from stages
order by display_order
