# Where the dashboard gets its deal data.
#
# 1. If Snowflake credentials are configured, query the live mart tables.
# 2. If they aren't (or the connection fails, e.g. an expired trial account),
#    read the saved snapshot CSV built by pipeline/build_snapshot.py.
#
# Returns (DataFrame, source) where source is "snowflake" or "snapshot",
# so the app can tell the viewer which one they're looking at.
from pathlib import Path

import pandas as pd

SNAPSHOT_PATH = Path(__file__).resolve().parent / "data" / "deals_snapshot.csv"

DEALS_QUERY = """
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
    FROM SIMPRO_REVOPS.MART.FCT_DEALS f
    LEFT JOIN SIMPRO_REVOPS.MART.DIM_STAGES s ON f.stage_id = s.stage_id
"""


def _snowflake_connect(**kwargs):
    # Imported here so the snapshot path works without the Snowflake driver
    import snowflake.connector
    return snowflake.connector.connect(**kwargs)


def _load_from_snowflake(sf, connect):
    conn = connect(
        account=sf["account"],
        user=sf["user"],
        password=sf["password"],
        warehouse=sf["warehouse"],
        database=sf["database"],
        role=sf["role"],
    )
    try:
        cur = conn.cursor()
        cur.execute(DEALS_QUERY)
        rows = cur.fetchall()
        cols = [c[0].lower() for c in cur.description]
        return pd.DataFrame(rows, columns=cols)
    finally:
        conn.close()


def _load_from_snapshot(path):
    df = pd.read_csv(path, dtype={"deal_id": str, "stage_id": str})
    # CSV stores booleans as text; the app needs real booleans for ~df["is_won"]
    for col in ["is_won", "is_lost"]:
        df[col] = df[col].astype(str).str.lower().eq("true")
    return df


def load_deals(secrets, snapshot_path=SNAPSHOT_PATH, connect=_snowflake_connect):
    sf = secrets.get("snowflake") if secrets else None
    if sf:
        try:
            return _load_from_snowflake(sf, connect), "snowflake"
        except Exception:
            pass  # fall through to the snapshot
    return _load_from_snapshot(snapshot_path), "snapshot"
