"""CorrelationId + Correlation — the product's core value (context: correlation).

A correlation is the crossing of several findings to reveal what no single
scanner sees. It is always deterministic and **never speculative**: a
correlation without source findings (evidence) is rejected.
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.asset.asset import AssetId
from hexa_sec.domain.correlation.correlation_type import CorrelationType
from hexa_sec.domain.correlation.impact_score import ImpactScore
from hexa_sec.domain.finding.finding import FindingId


@dataclass(frozen=True)
class CorrelationId:
    """An absolute identifier for a correlation."""

    value: str


@dataclass(frozen=True)
class Correlation:
    """A deterministic cross-finding insight."""

    correlation_id: CorrelationId
    type: CorrelationType
    assets: tuple[AssetId, ...]
    findings: tuple[FindingId, ...]
    impact: ImpactScore
    reason: str

    def __post_init__(self) -> None:
        if not self.findings:
            raise ValueError("correlation requires at least one source finding (evidence)")
        if not self.reason or not self.reason.strip():
            raise ValueError("correlation requires a plain-language reason")
