# Tests for streamlit/data_source.py: where the dashboard gets its data.
# With Snowflake credentials it queries Snowflake; without them (or if the
# connection fails) it reads the saved snapshot CSV.
import pandas as pd

import data_source

COLUMNS = ["deal_id", "deal_name", "amount", "stage_id", "stage_name", "win_probability",
           "close_date", "created_date", "is_won", "is_lost", "days_to_close",
           "days_in_pipeline", "display_order"]


def _write_snapshot(tmp_path):
    df = pd.DataFrame([{
        "deal_id": "1", "deal_name": "A", "amount": 100.0, "stage_id": "closedwon",
        "stage_name": "Closed won", "win_probability": 1.0, "close_date": "2025-01-10",
        "created_date": "2025-01-01", "is_won": True, "is_lost": False,
        "days_to_close": 9, "days_in_pipeline": 30, "display_order": 5,
    }])
    path = tmp_path / "deals_snapshot.csv"
    df.to_csv(path, index=False)
    return path


def test_uses_snapshot_when_no_snowflake_secrets(tmp_path):
    path = _write_snapshot(tmp_path)
    df, source = data_source.load_deals(secrets={}, snapshot_path=path)
    assert source == "snapshot"
    assert list(df.columns) == COLUMNS
    assert len(df) == 1


def test_falls_back_to_snapshot_when_snowflake_fails(tmp_path):
    path = _write_snapshot(tmp_path)

    def broken_connect(**kwargs):
        raise RuntimeError("trial account expired")

    secrets = {"snowflake": {"account": "x", "user": "x", "password": "x",
                             "warehouse": "x", "database": "x", "role": "x"}}
    df, source = data_source.load_deals(secrets=secrets, snapshot_path=path,
                                        connect=broken_connect)
    assert source == "snapshot"
    assert len(df) == 1


def test_snapshot_booleans_survive_csv(tmp_path):
    # is_won / is_lost must come back as real booleans: the app does ~df["is_won"]
    path = _write_snapshot(tmp_path)
    df, _ = data_source.load_deals(secrets={}, snapshot_path=path)
    assert df["is_won"].dtype == bool
    assert df["is_lost"].dtype == bool
