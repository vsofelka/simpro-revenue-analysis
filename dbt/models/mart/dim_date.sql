with date_spine as (
    select
        dateadd(day, seq4(), '2020-01-01'::date) as date_day
    from table(generator(rowcount => 3650))
)

select
    date_day,
    year(date_day)                                                    as year,
    month(date_day)                                                   as month_number,
    day(date_day)                                                     as day_of_month,
    quarter(date_day)                                                 as quarter,
    dayofweek(date_day)                                               as day_of_week,
    dayname(date_day)                                                 as day_name,
    monthname(date_day)                                               as month_name,
    case when dayofweek(date_day) in (0, 6) then true else false end  as is_weekend,
    date_trunc('month',   date_day)                                   as month_start_date,
    date_trunc('quarter', date_day)                                   as quarter_start_date
from date_spine
