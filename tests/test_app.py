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
