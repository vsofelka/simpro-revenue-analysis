# Tests for the row-building helpers in pipeline/hubspot_extract.py.
# These turn HubSpot API objects into plain tuples, so both the Snowflake load
# and the snapshot build can share them.
from types import SimpleNamespace

NOW = "2026-09-30 12:00:00"


def _deal(deal_id, contact_ids=(), **props):
    # Build a fake HubSpot deal object with only the attributes the code reads
    assoc = None
    if contact_ids:
        results = [SimpleNamespace(id=c) for c in contact_ids]
        assoc = {"contacts": SimpleNamespace(results=results)}
    return SimpleNamespace(id=deal_id, properties=props, associations=assoc)


def test_module_imports_without_snowflake_env(monkeypatch):
    # The snapshot build has no Snowflake account, so importing the module
    # must not require any SNOWFLAKE_* variables.
    for key in ["SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD",
                "SNOWFLAKE_WAREHOUSE", "SNOWFLAKE_DATABASE"]:
        monkeypatch.delenv(key, raising=False)
    import importlib
    import hubspot_extract
    importlib.reload(hubspot_extract)


def test_deal_rows_parses_fields():
    import hubspot_extract
    deal = _deal(
        101, contact_ids=[7, 8],
        dealname="TechForge Inc - Starter Plan", amount="12000",
        dealstage="closedwon", pipeline="default",
        closedate="2025-01-15T00:00:00Z", createdate="2024-11-20T08:30:00.000Z",
    )
    assert hubspot_extract.deal_rows([deal], NOW) == [(
        "101", "TechForge Inc - Starter Plan", 12000.0, "closedwon", "default",
        "2025-01-15", "2024-11-20 08:30:00", "7", NOW,
    )]


def test_deal_rows_handles_missing_values():
    import hubspot_extract
    deal = _deal(102, dealname="No Amount Deal", amount="", dealstage="appointmentscheduled",
                 pipeline="default", closedate=None, createdate=None)
    row = hubspot_extract.deal_rows([deal], NOW)[0]
    assert row[2] is None          # amount
    assert row[5] is None          # close date
    assert row[6] is None          # created at
    assert row[7] is None          # no associated contact


def test_stage_rows():
    import hubspot_extract
    stages = [{"stage_id": "closedwon", "stage_name": "Closed won", "pipeline_id": "default",
               "display_order": 5, "win_probability": 1.0}]
    assert hubspot_extract.stage_rows(stages, NOW) == [
        ("closedwon", "Closed won", "default", 5, 1.0, NOW)
    ]
