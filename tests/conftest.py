# Make the pipeline/ and streamlit/ folders importable from the tests
# (neither folder is a Python package, so pytest can't find them on its own).
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
sys.path.insert(0, str(ROOT / "streamlit"))
