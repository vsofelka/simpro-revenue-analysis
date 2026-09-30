# Checks the committed snapshot the live dashboard reads
# (built by pipeline/build_snapshot.py).
import json
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "streamlit" / "data"

APP_COLUMNS = ["deal_id", "deal_name", "amount", "stage_id", "stage_name", "win_probability",
               "close_date", "created_date", "is_won", "is_lost", "days_to_close",
               "days_in_pipeline", "display_order"]


def test_snapshot_has_every_column_the_app_uses():
    df = pd.read_csv(DATA / "deals_snapshot.csv")
    assert list(df.columns) == APP_COLUMNS


def test_snapshot_matches_its_info_file():
    df = pd.read_csv(DATA / "deals_snapshot.csv")
    info = json.loads((DATA / "snapshot_info.json").read_text())
    assert info["deal_count"] == len(df) > 0
    assert info["source"] == "HubSpot"


def test_every_deal_has_a_known_stage():
    # A deal whose stage didn't join to dim_stages would show a blank stage in every chart
    df = pd.read_csv(DATA / "deals_snapshot.csv")
    assert df["stage_name"].notna().all()
