# Runs the whole dashboard headless (no browser) with no Snowflake secrets,
# which is exactly the situation on the live demo after the trial expired.
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "streamlit" / "app.py"


def test_dashboard_renders_from_snapshot():
    at = AppTest.from_file(str(APP), default_timeout=60).run()
    assert not at.exception
    metrics = {m.label: m.value for m in at.metric}
    assert metrics["Total Deals"] == "226"
    assert any("saved snapshot" in c.value for c in at.caption)


def test_kpis_use_standard_revops_definitions():
    # Win rate counts closed deals only (72 won / 111 closed), not open ones;
    # open pipeline sums only deals still open (115 deals). Numbers are from
    # the saved snapshot in streamlit/data/.
    at = AppTest.from_file(str(APP), default_timeout=60).run()
    metrics = {m.label: m.value for m in at.metric}
    assert metrics["Win Rate"] == "64.9%"
    assert metrics["Open Pipeline"] == "$6,595,213"
    assert "Pipeline Value" not in metrics


def test_days_to_close_chart_title_matches_what_it_shows():
    # The chart only compares closed won vs closed lost; the data has no
    # stage history, so it must not claim to be "by stage".
    at = AppTest.from_file(str(APP), default_timeout=60).run()
    titles = [s.value for s in at.subheader]
    assert "Days to Close: Won vs Lost" in titles
    assert "Deal Velocity by Stage" not in titles
