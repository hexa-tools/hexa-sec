"""Tests for ScanId + Scan aggregate (context: scan, SEC-4).

Covers: creation, mandate binding, scope/level invariants, exclusions,
status transitions and immutability — the orchestration contract.
"""

from __future__ import annotations

from datetime import date

import pytest

from hexa_sec.domain.asset.asset import Asset
from hexa_sec.domain.asset.asset_type import AssetType
from hexa_sec.domain.consent.mandate import Mandate, MandateId, MandateLevel
from hexa_sec.domain.errors import (
    MandateExpiredError,
    MandateLevelError,
    MandateNotFoundError,
    MandateScopeError,
)
from hexa_sec.domain.scan.scan import Scan, ScanId
from hexa_sec.domain.scan.scan_depth import ScanDepth
from hexa_sec.domain.scan.scan_parameters import ScanParameters
from hexa_sec.domain.scan.scan_status import ScanStatus


def _mandate(level: MandateLevel = MandateLevel.STANDARD, targets: tuple[str, ...] = ("10.0.0.1",)) -> Mandate:
    return Mandate(
        mandate_id=MandateId("mnd_0001"),
        client="Acme Corp",
        targets=targets,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        level=level,
        signature="REF-2026-0001",
    )


def _asset(name: str = "10.0.0.1") -> Asset:
    return Asset(name=name, type=AssetType.HOST)


def _params(**overrides: object) -> ScanParameters:
    defaults: dict[str, object] = {
        "depth": ScanDepth.COMPLETE,
        "exclusions": (),
        "window": None,
    }
    defaults.update(overrides)
    return ScanParameters(**defaults)


def _scan(**overrides: object) -> Scan:
    defaults: dict[str, object] = {
        "scan_id": ScanId("scan_0001"),
        "mandate": _mandate(),
        "assets": (_asset(),),
        "vendors": ("nessus", "nuclei"),
        "parameters": _params(),
        "as_of": date(2026, 6, 1),
    }
    defaults.update(overrides)
    return Scan.create(**defaults)


def test_scan_creation() -> None:
    scan = _scan()
    assert scan.status is ScanStatus.PENDING
    assert scan.vendors == ("nessus", "nuclei")
    assert scan.assets == (_asset(),)
    assert scan.parameters.depth is ScanDepth.COMPLETE


def test_scan_exposes_mandate_id() -> None:
    scan = _scan()
    assert scan.mandate_id == MandateId("mnd_0001")


def test_scan_rejects_missing_mandate() -> None:
    with pytest.raises(MandateNotFoundError):
        _scan(mandate=None)


def test_scan_valid_at_start_date_boundary() -> None:
    # frontières : exactement au début de la validité du mandat
    scan = _scan(as_of=date(2026, 1, 1))
    assert scan.status is ScanStatus.PENDING


def test_scan_expired_before_start_date() -> None:
    # frontières : juste avant le début → expiré
    with pytest.raises(MandateExpiredError):
        _scan(as_of=date(2025, 12, 31))


def test_scan_valid_at_end_date_boundary() -> None:
    # frontières : exactement à la fin → encore valide
    scan = _scan(as_of=date(2026, 12, 31))
    assert scan.status is ScanStatus.PENDING


def test_scan_expired_at_end_date_plus_one() -> None:
    # frontières : le lendemain de la fin → expiré
    with pytest.raises(MandateExpiredError):
        _scan(as_of=date(2027, 1, 1))


def test_scan_rejects_asset_outside_mandate_scope() -> None:
    with pytest.raises(MandateScopeError):
        _scan(assets=(_asset("192.168.1.50"),))


def test_scan_offensive_depth_requires_offensive_mandate() -> None:
    with pytest.raises(MandateLevelError):
        _scan(parameters=_params(depth=ScanDepth.OFFENSIVE))


def test_scan_offensive_depth_with_offensive_mandate() -> None:
    scan = _scan(mandate=_mandate(level=MandateLevel.OFFENSIVE), parameters=_params(depth=ScanDepth.OFFENSIVE))
    assert scan.parameters.depth is ScanDepth.OFFENSIVE


def test_scan_rejects_scanning_an_excluded_host() -> None:
    with pytest.raises(ValueError):
        _scan(parameters=_params(exclusions=("10.0.0.1",)))


def test_scan_rejects_empty_assets() -> None:
    with pytest.raises(ValueError):
        _scan(assets=())


def test_scan_transitions_to_running_then_done() -> None:
    running = _scan().with_status(ScanStatus.RUNNING)
    assert running.status is ScanStatus.RUNNING
    assert running.with_status(ScanStatus.DONE).status is ScanStatus.DONE


def test_scan_transition_running_to_failed() -> None:
    assert _scan().with_status(ScanStatus.RUNNING).with_status(ScanStatus.FAILED).status is ScanStatus.FAILED


def test_scan_rejects_illegal_transition_done_to_pending() -> None:
    done = _scan().with_status(ScanStatus.RUNNING).with_status(ScanStatus.DONE)
    with pytest.raises(ValueError):
        done.with_status(ScanStatus.PENDING)


def test_scan_rejects_skipping_running() -> None:
    with pytest.raises(ValueError):
        _scan().with_status(ScanStatus.DONE)


def test_scan_rejects_failed_to_anything() -> None:
    failed = _scan().with_status(ScanStatus.RUNNING).with_status(ScanStatus.FAILED)
    with pytest.raises(ValueError):
        failed.with_status(ScanStatus.RUNNING)


def test_scan_is_immutable_on_transition() -> None:
    scan = _scan()
    running = scan.with_status(ScanStatus.RUNNING)
    assert scan.status is ScanStatus.PENDING
    assert running.status is ScanStatus.RUNNING
