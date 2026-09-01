"""Tests for ScanId + Scan (context: scan)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.asset.asset import AssetId
from hexa_sec.domain.consent.mandate import MandateId
from hexa_sec.domain.scan.scan import Scan, ScanId
from hexa_sec.domain.scan.scan_status import ScanStatus


def _scan(**overrides: object) -> Scan:
    defaults: dict[str, object] = {
        "scan_id": ScanId("scan_0001"),
        "mandate_id": MandateId("mnd_0001"),
        "assets": (AssetId("ast_0001"),),
        "vendors": ("nessus", "nuclei"),
    }
    defaults.update(overrides)
    return Scan(**defaults)


def test_scan_creation() -> None:
    scan = _scan()
    assert scan.status is ScanStatus.PENDING
    assert scan.vendors == ("nessus", "nuclei")
    assert scan.assets == (AssetId("ast_0001"),)


def test_scan_rejects_without_assets() -> None:
    with pytest.raises(ValueError):
        _scan(assets=())


def test_scan_rejects_without_mandate() -> None:
    with pytest.raises(ValueError):
        Scan(scan_id=ScanId("scan_0002"), mandate_id=None, assets=(AssetId("ast_0001"),), vendors=())


def test_scan_transition_to_done() -> None:
    scan = _scan()
    completed = scan.with_status(ScanStatus.DONE)
    assert completed.status is ScanStatus.DONE
    assert scan.status is ScanStatus.PENDING
