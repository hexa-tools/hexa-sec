"""Tests for the deterministic correlation checker (context: correlation, SEC-6)."""

from __future__ import annotations

from hexa_sec.domain.asset.asset import AssetId
from hexa_sec.domain.asset.asset_criticality import AssetCriticality
from hexa_sec.domain.correlation.correlation import Correlation
from hexa_sec.domain.correlation.correlation_checker import correlate
from hexa_sec.domain.correlation.correlation_context import CorrelationContext
from hexa_sec.domain.correlation.correlation_input import CorrelationInput
from hexa_sec.domain.correlation.correlation_type import CorrelationType
from hexa_sec.domain.correlation.finding_kind import FindingKind
from hexa_sec.domain.finding.finding import FindingId
from hexa_sec.domain.finding.severity import Severity

FINDINGS = iter(f"fnd_{i}" for i in range(1000))


def _sig(asset: str, kind: FindingKind, severity: Severity, detail: str = "") -> CorrelationInput:
    finding_id = FindingId(next(FINDINGS))
    return CorrelationInput(
        finding_id=finding_id,
        assets=(AssetId(asset),),
        kind=kind,
        severity=severity,
        detail=detail,
    )


def _types(correlations: tuple[Correlation, ...]) -> set[CorrelationType]:
    return {correlation.type for correlation in correlations}


def test_empty_inputs_yields_no_correlation() -> None:
    assert correlate((), CorrelationContext()) == ()


def test_attack_chain_on_same_asset() -> None:
    signals = (
        _sig("host1", FindingKind.VULNERABILITY, Severity.CRITICAL, "CVE-2024-0001"),
        _sig("host1", FindingKind.SQL_INJECTION, Severity.HIGH),
        _sig("host1", FindingKind.SECRET, Severity.CRITICAL),
    )
    correlations = correlate(signals, CorrelationContext())
    assert _types(correlations) == {CorrelationType.ATTACK_CHAIN}
    chain = correlations[0]
    assert len(chain.findings) == 3
    assert chain.assets == (AssetId("host1"),)
    assert chain.reason.strip()


def test_attack_chain_requires_all_three_kinds() -> None:
    signals = (
        _sig("host1", FindingKind.VULNERABILITY, Severity.CRITICAL, "CVE-2024-0001"),
        _sig("host1", FindingKind.SQL_INJECTION, Severity.HIGH),
    )
    assert correlate(signals, CorrelationContext()) == ()


def test_attack_chain_requires_severe_vulnerability() -> None:
    signals = (
        _sig("host1", FindingKind.VULNERABILITY, Severity.LOW),
        _sig("host1", FindingKind.SQL_INJECTION, Severity.HIGH),
        _sig("host1", FindingKind.SECRET, Severity.CRITICAL),
    )
    assert correlate(signals, CorrelationContext()) == ()


def test_exposure_at_threshold() -> None:
    signals = tuple(_sig("host1", FindingKind.EXPOSED_PORT, Severity.MEDIUM) for _ in range(3))
    assert _types(correlate(signals, CorrelationContext())) == {CorrelationType.EXPOSURE}


def test_exposure_below_threshold() -> None:
    signals = tuple(_sig("host1", FindingKind.EXPOSED_PORT, Severity.MEDIUM) for _ in range(2))
    assert correlate(signals, CorrelationContext()) == ()


def test_noise_reduction_when_many_low_findings() -> None:
    signals = tuple(_sig("host1", FindingKind.NOISE, Severity.LOW) for _ in range(10))
    assert _types(correlate(signals, CorrelationContext())) == {CorrelationType.NOISE_REDUCTION}


def test_noise_reduction_absent_when_a_high_finding_exists() -> None:
    signals = (_sig("host1", FindingKind.NOISE, Severity.LOW),) * 10 + (
        _sig("host1", FindingKind.VULNERABILITY, Severity.HIGH),
    )
    assert _types(correlate(signals, CorrelationContext())) != {CorrelationType.NOISE_REDUCTION}


def test_temporal_detects_new_exposure() -> None:
    previous = (_sig("host1", FindingKind.EXPOSED_PORT, Severity.MEDIUM),)
    current = previous + (_sig("host1", FindingKind.EXPOSED_PORT, Severity.MEDIUM),)
    correlations = correlate(current, CorrelationContext(previous=previous))
    assert _types(correlations) == {CorrelationType.TEMPORAL}


def test_temporal_absent_without_previous() -> None:
    current = (_sig("host1", FindingKind.EXPOSED_PORT, Severity.MEDIUM),)
    assert correlate(current, CorrelationContext()) == ()


def test_temporal_absent_when_nothing_new() -> None:
    previous = (_sig("host1", FindingKind.EXPOSED_PORT, Severity.MEDIUM),)
    current = previous
    assert correlate(current, CorrelationContext(previous=previous)) == ()


def test_compliance_when_frame_finding_present() -> None:
    signals = (_sig("host1", FindingKind.COMPLIANCE, Severity.MEDIUM),)
    assert _types(correlate(signals, CorrelationContext())) == {CorrelationType.COMPLIANCE}


def test_business_impact_derives_from_criticality() -> None:
    context = CorrelationContext(asset_criticalities={AssetId("host1"): AssetCriticality.ERP})
    signals = (_sig("host1", FindingKind.VULNERABILITY, Severity.CRITICAL),)
    assert _types(correlate(signals, context)) == {CorrelationType.BUSINESS_IMPACT}


def test_business_impact_absent_for_low_criticality() -> None:
    context = CorrelationContext(asset_criticalities={AssetId("host1"): AssetCriticality.PUBLIC})
    signals = (_sig("host1", FindingKind.VULNERABILITY, Severity.LOW),)
    assert correlate(signals, context) == ()


def test_business_impact_absent_when_criticality_unknown() -> None:
    # aucun asset mappé -> la criticité est inconnue, pas de business-impact
    signals = (_sig("host1", FindingKind.VULNERABILITY, Severity.CRITICAL),)
    assert correlate(signals, CorrelationContext()) == ()


def test_business_impact_absent_when_score_below_threshold() -> None:
    # catégorie « frontières » : une criticité non-publique mais une sévérité
    # faible donne un score < 0.5 -> pas de business-impact.
    context = CorrelationContext(asset_criticalities={AssetId("host1"): AssetCriticality.INTERNAL})
    signals = (_sig("host1", FindingKind.VULNERABILITY, Severity.LOW),)
    assert correlate(signals, context) == ()


def test_correlate_is_independent_of_input_order() -> None:
    # catégorie « ordre / déterminisme » : le même set dans un autre ordre
    # produit les mêmes corrélations (le checker trie).
    signals = (
        _sig("host1", FindingKind.VULNERABILITY, Severity.CRITICAL),
        _sig("host1", FindingKind.SQL_INJECTION, Severity.HIGH),
        _sig("host1", FindingKind.SECRET, Severity.CRITICAL),
    )
    forward = correlate(signals, CorrelationContext())
    reordered = correlate(tuple(reversed(signals)), CorrelationContext())
    assert forward == reordered


def test_correlate_is_deterministic_and_deduped() -> None:
    signals = (
        _sig("host1", FindingKind.VULNERABILITY, Severity.CRITICAL),
        _sig("host1", FindingKind.SQL_INJECTION, Severity.HIGH),
        _sig("host1", FindingKind.SECRET, Severity.CRITICAL),
    )
    first = correlate(signals, CorrelationContext())
    second = correlate(signals, CorrelationContext())
    assert first == second
    assert len(first) == len({c.correlation_id.value for c in first})
