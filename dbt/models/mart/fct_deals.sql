with deals as (
    select * from {{ ref('stg_deals') }}
),

stages as (
    select stage_id, stage_name, win_probability
    from {{ ref('dim_stages') }}
),

final as (
    select
        d.deal_id,
        d.deal_name,
        d.amount,
        d.pipeline_id,
        d.primary_contact_id                                          as contact_id,
        d.deal_stage                                                  as stage_id,
        s.stage_name,
        s.win_probability,
        d.close_date,
        d.created_at::date                                            as created_date,
        case when d.deal_stage = 'closedwon'  then true else false end as is_won,
        case when d.deal_stage = 'closedlost' then true else false end as is_lost,
        case
            when d.deal_stage in ('closedwon', 'closedlost')
            then datediff('day', d.created_at::date, d.close_date)
            else null
        end                                                            as days_to_close,
        datediff('day', d.created_at::date, current_date())           as days_in_pipeline
    from deals d
    left join stages s on d.deal_stage = s.stage_id
)

select * from final
