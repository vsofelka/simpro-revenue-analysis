with contacts as (
    select * from {{ ref('stg_contacts') }}
)

select
    contact_id,
    first_name,
    last_name,
    coalesce(first_name, '') || ' ' || coalesce(last_name, '') as full_name,
    email,
    company,
    lifecycle_stage,
    created_at
from contacts
