"""The deterministic correlation checker — the product's core (context: correlation).

Crosses normalized findings (CorrelationInput) into Correlations, per the six
deterministic families. Never speculative: it only emits when there is proof
(source findings) and always in plain language. A run that finds nothing returns
an empty tuple — no failure.
"""

from __future__ import annotations

from collections.abc import Sequence

from hexa_sec.domain.asset.asset import AssetId
from hexa_sec.domain.asset.asset_criticality import AssetCriticality
from hexa_sec.domain.correlation.correlation import Correlation, CorrelationId
from hexa_sec.domain.correlation.correlation_context import CorrelationContext
from hexa_sec.domain.correlation.correlation_input import CorrelationInput
from hexa_sec.domain.correlation.correlation_type import CorrelationType
from hexa_sec.domain.correlation.finding_kind import FindingKind
from hexa_sec.domain.correlation.impact_score import ImpactScore
from hexa_sec.domain.finding.finding import FindingId
from hexa_sec.domain.finding.severity import Severity

_ATTACK_KINDS = (FindingKind.VULNERABILITY, FindingKind.SQL_INJECTION, FindingKind.SECRET)
_SEVERE = (Severity.HIGH, Severity.CRITICAL)
_LOW = (Severity.LOW, Severity.INFO)


def correlate(
    inputs: Sequence[CorrelationInput],
    context: CorrelationContext,
) -> tuple[Correlation, ...]:
    """Return the deterministic correlations for ``inputs``, deduplicated."""
    detectors = (
        _attack_chain,
        _exposure,
        _noise_reduction,
        _temporal,
        _compliance,
        _business_impact,
    )
    grouped = _group_by_asset(inputs)
    correlations: list[Correlation] = []

    for asset_value in sorted(grouped):
        signals = grouped[asset_value]
        for detector in detectors:
            correlation = detector(asset_value, signals, context)
            if correlation is not None:
                correlations.append(correlation)

    return tuple(sorted(set(correlations), key=lambda c: c.correlation_id.value))


def _group_by_asset(inputs: Sequence[CorrelationInput]) -> dict[str, list[CorrelationInput]]:
    grouped: dict[str, list[CorrelationInput]] = {}
    for signal in inputs:
        for asset in signal.assets:
            grouped.setdefault(asset.value, []).append(signal)
    return grouped


def _id(
    correlation_type: CorrelationType, assets: tuple[AssetId, ...], findings: tuple[FindingId, ...]
) -> CorrelationId:
    asset_part = ",".join(sorted(asset.value for asset in assets))
    finding_part = ",".join(sorted(finding.value for finding in findings))
    return CorrelationId(f"cor:{correlation_type.value}:{asset_part}:{finding_part}")


def _findings_of(signals: Sequence[CorrelationInput]) -> tuple[FindingId, ...]:
    return tuple(sorted((signal.finding_id for signal in signals), key=lambda f: f.value))


def _attack_chain(
    asset_value: str, signals: list[CorrelationInput], _context: CorrelationContext
) -> Correlation | None:
    kinds = {signal.kind for signal in signals}
    severe_vulnerability = any(
        signal.kind is FindingKind.VULNERABILITY and signal.severity in _SEVERE
        for signal in signals
    )
    if not (
        severe_vulnerability and FindingKind.SQL_INJECTION in kinds and FindingKind.SECRET in kinds
    ):
        return None
    participating = [s for s in signals if s.kind in _ATTACK_KINDS]
    findings = _findings_of(participating)
    reason = (
        f"Attack chain on {asset_value}: critical vulnerability plus SQL injection "
        f"and a committed secret on the same host."
    )
    return Correlation(
        _id(CorrelationType.ATTACK_CHAIN, (AssetId(asset_value),), findings),
        CorrelationType.ATTACK_CHAIN,
        (AssetId(asset_value),),
        findings,
        ImpactScore(0.9),
        reason,
    )


def _exposure(
    asset_value: str, signals: list[CorrelationInput], context: CorrelationContext
) -> Correlation | None:
    exposed = [s for s in signals if s.kind is FindingKind.EXPOSED_PORT]
    if len(exposed) < context.exposure_open_ports:
        return None
    findings = _findings_of(exposed)
    reason = f"{len(exposed)} ports exposed on {asset_value} without necessity."
    return Correlation(
        _id(CorrelationType.EXPOSURE, (AssetId(asset_value),), findings),
        CorrelationType.EXPOSURE,
        (AssetId(asset_value),),
        findings,
        ImpactScore(0.6),
        reason,
    )


def _noise_reduction(
    asset_value: str, signals: list[CorrelationInput], context: CorrelationContext
) -> Correlation | None:
    lows = [s for s in signals if s.kind is FindingKind.NOISE or s.severity in _LOW]
    highs = [s for s in signals if s.severity in _SEVERE]
    if len(lows) < context.noise_count or highs:
        return None
    findings = _findings_of(lows)
    reason = f"{len(lows)} low-severity findings on {asset_value} with no real risk."
    return Correlation(
        _id(CorrelationType.NOISE_REDUCTION, (AssetId(asset_value),), findings),
        CorrelationType.NOISE_REDUCTION,
        (AssetId(asset_value),),
        findings,
        ImpactScore(0.2),
        reason,
    )


def _temporal(
    asset_value: str, signals: list[CorrelationInput], context: CorrelationContext
) -> Correlation | None:
    if not context.previous:
        return None
    previous_ids = {signal.finding_id for signal in context.previous}
    new = [
        s
        for s in signals
        if s.finding_id not in previous_ids
        and s.kind in (FindingKind.EXPOSED_PORT, FindingKind.VULNERABILITY)
    ]
    if not new:
        return None
    findings = _findings_of(new)
    kinds = sorted({s.kind.value for s in new})
    reason = f"New {', '.join(kinds)} exposure since the previous scan on {asset_value}."
    return Correlation(
        _id(CorrelationType.TEMPORAL, (AssetId(asset_value),), findings),
        CorrelationType.TEMPORAL,
        (AssetId(asset_value),),
        findings,
        ImpactScore(0.5),
        reason,
    )


def _compliance(
    asset_value: str, signals: list[CorrelationInput], _context: CorrelationContext
) -> Correlation | None:
    failing = [s for s in signals if s.kind in (FindingKind.COMPLIANCE, FindingKind.MISCONFIG)]
    if not failing:
        return None
    findings = _findings_of(failing)
    reason = f"{len(failing)} finding(s) failing a compliance framework on {asset_value}."
    return Correlation(
        _id(CorrelationType.COMPLIANCE, (AssetId(asset_value),), findings),
        CorrelationType.COMPLIANCE,
        (AssetId(asset_value),),
        findings,
        ImpactScore(0.7),
        reason,
    )


def _business_impact(
    asset_value: str, signals: list[CorrelationInput], context: CorrelationContext
) -> Correlation | None:
    criticality = context.criticality_of(AssetId(asset_value))
    if criticality is None:
        return None
    if criticality is AssetCriticality.PUBLIC:
        return None
    top_severity = max((signal.severity.rank for signal in signals), default=0)
    score = (criticality.weight / 5.0) * 0.5 + (top_severity / 4.0) * 0.5
    if score < 0.5:
        return None
    participating = [s for s in signals if s.severity.rank == top_severity]
    findings = _findings_of(participating)
    reason = (
        f"Business impact on {asset_value} (criticality {criticality.value}, "
        f"severity rank {top_severity})."
    )
    return Correlation(
        _id(CorrelationType.BUSINESS_IMPACT, (AssetId(asset_value),), findings),
        CorrelationType.BUSINESS_IMPACT,
        (AssetId(asset_value),),
        findings,
        ImpactScore(score),
        reason,
    )
