import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from hubspot import HubSpot
import snowflake.connector

load_dotenv()

HUBSPOT_ACCESS_TOKEN = os.environ['HUBSPOT_ACCESS_TOKEN']
SNOWFLAKE_ACCOUNT    = os.environ['SNOWFLAKE_ACCOUNT']
SNOWFLAKE_USER       = os.environ['SNOWFLAKE_USER']
SNOWFLAKE_PASSWORD   = os.environ['SNOWFLAKE_PASSWORD']
SNOWFLAKE_WAREHOUSE  = os.environ['SNOWFLAKE_WAREHOUSE']
SNOWFLAKE_DATABASE   = os.environ['SNOWFLAKE_DATABASE']
SNOWFLAKE_ROLE       = os.environ.get('SNOWFLAKE_ROLE', 'ACCOUNTADMIN')


def get_snowflake_conn():
    return snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        role=SNOWFLAKE_ROLE,
    )


def setup_raw_schema(conn):
    cur = conn.cursor()
    cur.execute("CREATE SCHEMA IF NOT EXISTS RAW")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS RAW.HUBSPOT_DEALS (
            DEAL_ID            VARCHAR,
            DEAL_NAME          VARCHAR,
            AMOUNT             FLOAT,
            DEAL_STAGE         VARCHAR,
            PIPELINE_ID        VARCHAR,
            CLOSE_DATE         DATE,
            CREATED_AT         TIMESTAMP_NTZ,
            PRIMARY_CONTACT_ID VARCHAR,
            EXTRACTED_AT       TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS RAW.HUBSPOT_CONTACTS (
            CONTACT_ID      VARCHAR,
            FIRST_NAME      VARCHAR,
            LAST_NAME       VARCHAR,
            EMAIL           VARCHAR,
            COMPANY         VARCHAR,
            LIFECYCLE_STAGE VARCHAR,
            CREATED_AT      TIMESTAMP_NTZ,
            EXTRACTED_AT    TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS RAW.HUBSPOT_STAGES (
            STAGE_ID        VARCHAR,
            STAGE_NAME      VARCHAR,
            PIPELINE_ID     VARCHAR,
            DISPLAY_ORDER   INTEGER,
            WIN_PROBABILITY FLOAT,
            EXTRACTED_AT    TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
    """)
    conn.commit()
    print("RAW schema and tables ready")


def _paginate(api_fn, properties, associations=None):
    results, after = [], None
    while True:
        kwargs = dict(limit=100, properties=properties)
        if after:
            kwargs['after'] = after
        if associations:
            kwargs['associations'] = associations
        page = api_fn(**kwargs)
        results.extend(page.results)
        if not page.paging or not page.paging.next:
            break
        after = page.paging.next.after
    return results


def extract_deals(client):
    deals = _paginate(
        client.crm.deals.basic_api.get_page,
        properties=['dealname', 'amount', 'dealstage', 'closedate', 'createdate', 'pipeline'],
        associations=['contacts'],
    )
    print(f"Extracted {len(deals)} deals")
    return deals


def extract_contacts(client):
    contacts = _paginate(
        client.crm.contacts.basic_api.get_page,
        properties=['firstname', 'lastname', 'email', 'company', 'lifecyclestage', 'createdate'],
    )
    print(f"Extracted {len(contacts)} contacts")
    return contacts


def extract_stages(client):
    stages = []
    response = client.crm.pipelines.pipelines_api.get_all(object_type='deals')
    for pipeline in response.results:
        for stage in pipeline.stages:
            probability = float(stage.metadata.get('probability', 0)) if stage.metadata else 0.0
            stages.append({
                'stage_id':        stage.id,
                'stage_name':      stage.label,
                'pipeline_id':     pipeline.id,
                'display_order':   stage.display_order,
                'win_probability': probability,
            })
    print(f"Extracted {len(stages)} pipeline stages")
    return stages


def _parse_date(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace('Z', '+00:00')).strftime('%Y-%m-%d')
    except Exception:
        return None


def _parse_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return None


def load_deals(conn, deals):
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE RAW.HUBSPOT_DEALS")
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    rows = []
    for d in deals:
        p = d.properties
        contact_id = None
        if d.associations and 'contacts' in d.associations:
            items = d.associations['contacts'].results
            if items:
                contact_id = str(items[0].id)
        rows.append((
            str(d.id),
            p.get('dealname'),
            float(p['amount']) if p.get('amount') else None,
            p.get('dealstage'),
            p.get('pipeline'),
            _parse_date(p.get('closedate')),
            _parse_ts(p.get('createdate')),
            contact_id,
            now,
        ))
    cur.executemany(
        "INSERT INTO RAW.HUBSPOT_DEALS VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        rows,
    )
    conn.commit()
    print(f"Loaded {len(rows)} deals")


def load_contacts(conn, contacts):
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE RAW.HUBSPOT_CONTACTS")
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    rows = []
    for c in contacts:
        p = c.properties
        rows.append((
            str(c.id),
            p.get('firstname'),
            p.get('lastname'),
            p.get('email'),
            p.get('company'),
            p.get('lifecyclestage'),
            _parse_ts(p.get('createdate')),
            now,
        ))
    cur.executemany(
        "INSERT INTO RAW.HUBSPOT_CONTACTS VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        rows,
    )
    conn.commit()
    print(f"Loaded {len(rows)} contacts")


def load_stages(conn, stages):
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE RAW.HUBSPOT_STAGES")
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    rows = [(s['stage_id'], s['stage_name'], s['pipeline_id'],
             s['display_order'], s['win_probability'], now) for s in stages]
    cur.executemany(
        "INSERT INTO RAW.HUBSPOT_STAGES VALUES (%s,%s,%s,%s,%s,%s)",
        rows,
    )
    conn.commit()
    print(f"Loaded {len(rows)} stages")


def main():
    client = HubSpot(access_token=HUBSPOT_ACCESS_TOKEN)
    conn   = get_snowflake_conn()

    setup_raw_schema(conn)

    deals    = extract_deals(client)
    contacts = extract_contacts(client)
    stages   = extract_stages(client)

    load_deals(conn, deals)
    load_contacts(conn, contacts)
    load_stages(conn, stages)

    conn.close()
    print("Extraction complete!")


if __name__ == '__main__':
    main()
