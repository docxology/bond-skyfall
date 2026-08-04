"""Pytest configuration for skyfall tests."""

import os
import sys
from pathlib import Path

# Force headless backend for matplotlib in tests.
os.environ.setdefault("MPLBACKEND", "Agg")

# Add src/ so the documented per-project pytest command works from a clean env.
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
for _path in (SRC,):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))
