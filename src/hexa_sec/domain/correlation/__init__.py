"""Bound context 4 — Correlation (the product's core value)."""

from __future__ import annotations

from hexa_sec.domain.correlation.correlation import Correlation, CorrelationId
from hexa_sec.domain.correlation.correlation_checker import correlate
from hexa_sec.domain.correlation.correlation_context import CorrelationContext
from hexa_sec.domain.correlation.correlation_input import CorrelationInput
from hexa_sec.domain.correlation.correlation_type import CorrelationType
from hexa_sec.domain.correlation.finding_kind import FindingKind
from hexa_sec.domain.correlation.impact_score import ImpactLevel, ImpactScore

__all__ = [
    "Correlation",
    "CorrelationContext",
    "CorrelationId",
    "CorrelationInput",
    "CorrelationType",
    "FindingKind",
    "ImpactLevel",
    "ImpactScore",
    "correlate",
]
