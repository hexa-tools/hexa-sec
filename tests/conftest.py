"""Pytest conftest — puts the repo root (with hexa_guard.py) on sys.path."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

for directory in (REPO_ROOT, REPO_ROOT / "src"):
    value = str(directory)
    if value not in sys.path:
        sys.path.insert(0, value)
