"""Tests for ScanParameters (context: scan)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.scan.scan_depth import ScanDepth
from hexa_sec.domain.scan.scan_parameters import ScanParameters
from hexa_sec.domain.scan.scan_window import ScanWindow


def test_scan_parameters_creation() -> None:
    parameters = ScanParameters(depth=ScanDepth.COMPLETE)
    assert parameters.depth is ScanDepth.COMPLETE
    assert parameters.exclusions == ()
    assert parameters.window is None


def test_scan_parameters_with_exclusions_and_window() -> None:
    parameters = ScanParameters(
        depth=ScanDepth.QUICK,
        exclusions=("10.0.0.99",),
        window=ScanWindow(start_hour=22, end_hour=6),
    )
    assert parameters.exclusions == ("10.0.0.99",)
    assert parameters.window is not None


def test_scan_parameters_rejects_empty_exclusion() -> None:
    with pytest.raises(ValueError):
        ScanParameters(depth=ScanDepth.QUICK, exclusions=("  ",))
