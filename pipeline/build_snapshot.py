"""
build_snapshot.py — rebuild the data the live dashboard reads, without Snowflake.

Why this exists: the Streamlit dashboard originally queried Snowflake directly.
When the Snowflake trial account expired, the live app had no data. This script
runs the same pipeline against DuckDB (a free database that lives in a single
local file) and saves the result as a small CSV that ships with the repo, so the
live demo keeps working without any cloud account.

Steps:
  1. Pull deals and pipeline stages from HubSpot (same extract code as the
     Snowflake pipeline, in hubspot_extract.py).
  2. Load them into RAW tables in a local DuckDB file, same columns as Snowflake.
  3. Run the existing dbt models on DuckDB (only fct_deals and what it depends on).
  4. Export the columns the dashboard uses to streamlit/data/deals_snapshot.csv,
     plus snapshot_info.json (build date and row count).

Run from the repo root:
  python pipeline/build_snapshot.py
Needs HUBSPOT_ACCESS_TOKEN in .env, plus dbt-duckdb (in requirements.txt).
"""
import json
import os
import sys
from datetime import date
from pathlib import Path

import duckdb
from dotenv import load_dotenv
from dbt.cli.main import dbtRunner
from hubspot import HubSpot

from hubspot_extract import _now, deal_rows, extract_deals, extract_stages, stage_rows

ROOT = Path(__file__).resolve().parents[1]
DBT_DIR = ROOT / "dbt"
DB_PATH = DBT_DIR / "simpro_snapshot.duckdb"   # gitignored scratch database
OUT_DIR = ROOT / "streamlit" / "data"

# The dbt sources read their database name from SNOWFLAKE_DATABASE. In DuckDB the
# "database" is the file name without .duckdb, so point the variable at that.
DB_NAME = DB_PATH.stem

EXPORT_QUERY = f"""
    SELECT
        f.deal_id,
        f.deal_name,
        f.amount,
        f.stage_id,
        f.stage_name,
        f.win_probability,
        f.close_date,
        f.created_date,
        f.is_won,
        f.is_lost,
        f.days_to_close,
        f.days_in_pipeline,
        s.display_order
    FROM {DB_NAME}.MART.fct_deals f
    LEFT JOIN {DB_NAME}.MART.dim_stages s ON f.stage_id = s.stage_id
    ORDER BY f.created_date, f.deal_id
"""


def load_raw(deals, stages):
    # Start from an empty file each time so old rows never leak into a new snapshot
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = duckdb.connect(str(DB_PATH))
    con.execute("CREATE SCHEMA RAW")
    con.execute("""
        CREATE TABLE RAW.HUBSPOT_DEALS (
            DEAL_ID VARCHAR, DEAL_NAME VARCHAR, AMOUNT DOUBLE, DEAL_STAGE VARCHAR,
            PIPELINE_ID VARCHAR, CLOSE_DATE DATE, CREATED_AT TIMESTAMP,
            PRIMARY_CONTACT_ID VARCHAR, EXTRACTED_AT TIMESTAMP
        )
    """)
    con.execute("""
        CREATE TABLE RAW.HUBSPOT_STAGES (
            STAGE_ID VARCHAR, STAGE_NAME VARCHAR, PIPELINE_ID VARCHAR,
            DISPLAY_ORDER INTEGER, WIN_PROBABILITY DOUBLE, EXTRACTED_AT TIMESTAMP
        )
    """)
    now = _now()
    # DuckDB uses ? placeholders (Snowflake's connector uses %s)
    con.executemany("INSERT INTO RAW.HUBSPOT_DEALS VALUES (?,?,?,?,?,?,?,?,?)",
                    deal_rows(deals, now))
    con.executemany("INSERT INTO RAW.HUBSPOT_STAGES VALUES (?,?,?,?,?,?)",
                    stage_rows(stages, now))
    con.close()


def run_dbt():
    os.environ["SNAPSHOT_DB_PATH"] = str(DB_PATH)
    os.environ["SNOWFLAKE_DATABASE"] = DB_NAME
    # "build" = run the models and their schema tests; "+fct_deals" = fct_deals
    # and everything upstream of it (staging views, dim_stages)
    result = dbtRunner().invoke([
        "build", "--select", "+fct_deals",
        "--project-dir", str(DBT_DIR),
        "--profiles-dir", str(DBT_DIR / "profiles"),
    ])
    if not result.success:
        sys.exit("dbt build failed - see the output above")


def export_snapshot():
    # Same settings as dbt's connection: dbt (running in this process) still holds
    # the file open, and DuckDB refuses a second connection with different settings
    con = duckdb.connect(str(DB_PATH))
    df = con.execute(EXPORT_QUERY).df()
    con.close()
    # DuckDB keeps each column's original capitalisation (RAW columns are upper
    # case, dbt aliases lower case); the app expects all lower case, as it does
    # for Snowflake results
    df.columns = [c.lower() for c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_DIR / "deals_snapshot.csv", index=False)
    info = {"source": "HubSpot", "built_on": date.today().isoformat(), "deal_count": len(df)}
    (OUT_DIR / "snapshot_info.json").write_text(json.dumps(info, indent=2) + "\n")
    print(f"Saved {len(df)} deals to {OUT_DIR / 'deals_snapshot.csv'}")


def main():
    load_dotenv(ROOT / ".env")
    client = HubSpot(access_token=os.environ["HUBSPOT_ACCESS_TOKEN"])
    deals = extract_deals(client)
    stages = extract_stages(client)
    load_raw(deals, stages)
    run_dbt()
    export_snapshot()


if __name__ == "__main__":
    main()
