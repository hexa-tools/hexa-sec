"""Tests for CorrelateService (US-2 deterministic correlation)."""

from __future__ import annotations

import pytest

from hexa_sec.application.ports.driving.correlate.correlate_service_port import CorrelateCommand
from hexa_sec.application.service.correlate_service import CorrelateService
from hexa_sec.domain.asset.asset import AssetId
from hexa_sec.domain.asset.asset_criticality import AssetCriticality
from hexa_sec.domain.correlation.correlation_input import CorrelationInput
from hexa_sec.domain.correlation.correlation_type import CorrelationType
from hexa_sec.domain.correlation.finding_kind import FindingKind
from hexa_sec.domain.finding.finding import FindingId
from hexa_sec.domain.finding.severity import Severity


def _signal(
    asset: str,
    kind: FindingKind,
    severity: Severity,
    finding_id: str,
    detail: str = "",
) -> CorrelationInput:
    return CorrelationInput(
        finding_id=FindingId(finding_id),
        assets=(AssetId(asset),),
        kind=kind,
        severity=severity,
        detail=detail,
    )


def _command(**overrides: object) -> CorrelateCommand:
    defaults: dict[str, object] = {
        "scan_id": "scan_0001",
        "signals": (),
        "previous": (),
        "asset_criticalities": {},
        "exposure_open_ports": 3,
        "noise_count": 10,
    }
    defaults.update(overrides)
    return CorrelateCommand(**defaults)  # type: ignore[arg-type]


def test_empty_signals_yield_no_correlation() -> None:
    result = CorrelateService().correlate(_command())
    assert result["scan_id"] == "scan_0001"
    assert result["correlations"] == []


def test_attack_chain_detected() -> None:
    command = _command(
        signals=(
            _signal(
                "host1", FindingKind.VULNERABILITY, Severity.CRITICAL, "fnd_1", "CVE-2024-0001"
            ),
            _signal("host1", FindingKind.SQL_INJECTION, Severity.HIGH, "fnd_2"),
            _signal("host1", FindingKind.SECRET, Severity.CRITICAL, "fnd_3"),
        )
    )
    result = CorrelateService().correlate(command)
    assert len(result["correlations"]) == 1
    record = result["correlations"][0]
    assert record["type"] == CorrelationType.ATTACK_CHAIN.value
    assert record["reason"].strip()
    assert set(record["findings"]) == {"fnd_1", "fnd_2", "fnd_3"}


def test_exposure_detected() -> None:
    signals = tuple(
        _signal("host1", FindingKind.EXPOSED_PORT, Severity.MEDIUM, f"fnd_{i}", str(i))
        for i in range(4)
    )
    result = CorrelateService().correlate(_command(signals=signals))
    assert result["correlations"][0]["type"] == CorrelationType.EXPOSURE.value


def test_noise_reduction_detected() -> None:
    signals = tuple(
        _signal("host1", FindingKind.NOISE, Severity.LOW, f"fnd_{i}", str(i)) for i in range(11)
    )
    result = CorrelateService().correlate(
        _command(signals=signals, noise_count=10, exposure_open_ports=999)
    )
    assert result["correlations"][0]["type"] == CorrelationType.NOISE_REDUCTION.value


def test_temporal_detected() -> None:
    current = (_signal("host1", FindingKind.EXPOSED_PORT, Severity.HIGH, "fnd_cur"),)
    previous = (_signal("host1", FindingKind.NOISE, Severity.LOW, "fnd_prev"),)
    result = CorrelateService().correlate(_command(signals=current, previous=previous))
    assert result["correlations"][0]["type"] == CorrelationType.TEMPORAL.value


def test_compliance_detected() -> None:
    signal = _signal("host1", FindingKind.COMPLIANCE, Severity.HIGH, "fnd_1", "iso_27001")
    result = CorrelateService().correlate(_command(signals=(signal,)))
    assert result["correlations"][0]["type"] == CorrelationType.COMPLIANCE.value


def test_business_impact_detected() -> None:
    signal = _signal("host1", FindingKind.VULNERABILITY, Severity.CRITICAL, "fnd_1")
    result = CorrelateService().correlate(
        _command(
            signals=(signal,),
            asset_criticalities={AssetId("host1"): AssetCriticality.ERP},
        )
    )
    assert result["correlations"][0]["type"] == CorrelationType.BUSINESS_IMPACT.value


# --- Catégorie: stabilité / déterminisme (reproductible) + frontières -------
def test_correlate_is_deterministic() -> None:
    command = _command(
        signals=(
            _signal(
                "host1", FindingKind.VULNERABILITY, Severity.CRITICAL, "fnd_1", "CVE-2024-0001"
            ),
            _signal("host1", FindingKind.SQL_INJECTION, Severity.HIGH, "fnd_2"),
            _signal("host1", FindingKind.SECRET, Severity.CRITICAL, "fnd_3"),
        )
    )
    first = CorrelateService().correlate(command)
    second = CorrelateService().correlate(command)
    assert first == second


def test_correlate_rejects_invalid_threshold() -> None:
    with pytest.raises(ValueError):
        CorrelateService().correlate(_command(signals=(), exposure_open_ports=0, noise_count=10))
    with pytest.raises(ValueError):
        CorrelateService().correlate(_command(signals=(), exposure_open_ports=3, noise_count=0))
