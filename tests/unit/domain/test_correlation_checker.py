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
from hexa_sec.domain.correlation.impact_score import ImpactScore
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
    correlations = correlate(signals, CorrelationContext())
    assert _types(correlations) == {CorrelationType.EXPOSURE}
    assert correlations[0].assets == (AssetId("host1"),)


def test_exposure_below_threshold() -> None:
    signals = tuple(_sig("host1", FindingKind.EXPOSED_PORT, Severity.MEDIUM) for _ in range(2))
    assert correlate(signals, CorrelationContext()) == ()


def test_noise_reduction_when_many_low_findings() -> None:
    signals = tuple(_sig("host1", FindingKind.NOISE, Severity.LOW) for _ in range(10))
    correlations = correlate(signals, CorrelationContext())
    assert _types(correlations) == {CorrelationType.NOISE_REDUCTION}
    assert correlations[0].assets == (AssetId("host1"),)


def test_noise_reduction_counts_low_severity_of_any_kind() -> None:
    signals = tuple(_sig("host1", FindingKind.LOGIN, Severity.LOW) for _ in range(10))
    correlations = correlate(signals, CorrelationContext())
    assert _types(correlations) == {CorrelationType.NOISE_REDUCTION}
    assert correlations[0].assets == (AssetId("host1"),)


def test_noise_reduction_ignores_medium_severity_of_any_kind() -> None:
    signals = tuple(_sig("host1", FindingKind.LOGIN, Severity.MEDIUM) for _ in range(10))
    assert correlate(signals, CorrelationContext()) == ()


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
    assert correlations[0].assets == (AssetId("host1"),)


def test_temporal_reason_lists_new_kinds_sorted() -> None:
    previous = (_sig("host1", FindingKind.EXPOSED_PORT, Severity.MEDIUM),)
    new_exposure = _sig("host1", FindingKind.EXPOSED_PORT, Severity.MEDIUM)
    new_vulnerability = _sig("host1", FindingKind.VULNERABILITY, Severity.HIGH)
    current = previous + (new_exposure, new_vulnerability)
    correlations = correlate(current, CorrelationContext(previous=previous))
    assert _types(correlations) == {CorrelationType.TEMPORAL}
    temporal = correlations[0]
    expected = "New exposed_port, vulnerability exposure since the previous scan on host1."
    assert temporal.reason == expected


def test_temporal_absent_without_previous() -> None:
    current = (_sig("host1", FindingKind.EXPOSED_PORT, Severity.MEDIUM),)
    assert correlate(current, CorrelationContext()) == ()


def test_temporal_absent_when_nothing_new() -> None:
    previous = (_sig("host1", FindingKind.EXPOSED_PORT, Severity.MEDIUM),)
    current = previous
    assert correlate(current, CorrelationContext(previous=previous)) == ()


def test_compliance_when_frame_finding_present() -> None:
    signals = (_sig("host1", FindingKind.COMPLIANCE, Severity.MEDIUM),)
    correlations = correlate(signals, CorrelationContext())
    assert _types(correlations) == {CorrelationType.COMPLIANCE}
    assert correlations[0].assets == (AssetId("host1"),)


def test_business_impact_derives_from_criticality() -> None:
    context = CorrelationContext(asset_criticalities={AssetId("host1"): AssetCriticality.ERP})
    signals = (_sig("host1", FindingKind.VULNERABILITY, Severity.CRITICAL),)
    correlations = correlate(signals, context)
    assert _types(correlations) == {CorrelationType.BUSINESS_IMPACT}
    business = correlations[0]
    assert business.assets == (AssetId("host1"),)
    assert business.impact == ImpactScore(1.0)
    assert business.reason == "Business impact on host1 (criticality erp, severity rank 4)."


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


def test_correlate_sorts_results_by_correlation_id() -> None:
    signals = tuple(_sig("host1", FindingKind.EXPOSED_PORT, Severity.MEDIUM) for _ in range(3)) + (
        _sig("host1", FindingKind.COMPLIANCE, Severity.MEDIUM),
    )
    correlations = correlate(signals, CorrelationContext())
    assert len(correlations) == 2
    assert [c.type for c in correlations] == [
        CorrelationType.COMPLIANCE,
        CorrelationType.EXPOSURE,
    ]
    assert [c.correlation_id.value for c in correlations] == sorted(
        c.correlation_id.value for c in correlations
    )


def test_correlation_id_embeds_sorted_assets_and_findings() -> None:
    signals = (
        CorrelationInput(
            finding_id=FindingId("fnd_c"),
            kind=FindingKind.VULNERABILITY,
            severity=Severity.CRITICAL,
            assets=(AssetId("host1"),),
        ),
        CorrelationInput(
            finding_id=FindingId("fnd_a"),
            kind=FindingKind.SQL_INJECTION,
            severity=Severity.HIGH,
            assets=(AssetId("host1"),),
        ),
        CorrelationInput(
            finding_id=FindingId("fnd_b"),
            kind=FindingKind.SECRET,
            severity=Severity.CRITICAL,
            assets=(AssetId("host1"),),
        ),
    )
    correlations = correlate(signals, CorrelationContext())
    assert len(correlations) == 1
    chain = correlations[0]
    assert chain.correlation_id.value == "cor:attack-chain:host1:fnd_a,fnd_b,fnd_c"
    assert chain.assets == (AssetId("host1"),)
    assert chain.findings == (FindingId("fnd_a"), FindingId("fnd_b"), FindingId("fnd_c"))


def test_business_impact_emitted_at_exact_threshold_boundary() -> None:
    context = CorrelationContext(asset_criticalities={AssetId("host1"): AssetCriticality.ERP})
    signals = (_sig("host1", FindingKind.VULNERABILITY, Severity.INFO),)
    correlations = correlate(signals, context)
    assert _types(correlations) == {CorrelationType.BUSINESS_IMPACT}
    assert correlations[0].impact == ImpactScore(0.5)
