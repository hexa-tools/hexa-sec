"""Tests for Snapshot (context: temporal)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.temporal.snapshot import Snapshot


def test_snapshot_creation() -> None:
    snapshot = Snapshot(scan_id="scan_0001", taken_on="2026-01-01")
    assert snapshot.scan_id == "scan_0001"


def test_snapshot_rejects_empty_scan_id() -> None:
    with pytest.raises(ValueError):
        Snapshot(scan_id="", taken_on="2026-01-01")
