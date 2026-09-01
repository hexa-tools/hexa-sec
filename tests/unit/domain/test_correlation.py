"""Tests for CorrelationId + Correlation (context: correlation)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.asset.asset import AssetId
from hexa_sec.domain.correlation.correlation import Correlation, CorrelationId
from hexa_sec.domain.correlation.correlation_type import CorrelationType
from hexa_sec.domain.correlation.impact_score import ImpactScore
from hexa_sec.domain.finding.finding import FindingId


def test_correlation_creation() -> None:
    finding_id = FindingId("fnd_0001")
    correlation = Correlation(
        correlation_id=CorrelationId("cor_0001"),
        type=CorrelationType.ATTACK_CHAIN,
        assets=(AssetId("ast_0001"),),
        findings=(finding_id,),
        impact=ImpactScore(value=0.9),
        reason="Critical CVE plus exposed SQLi surface on the same host.",
    )
    assert correlation.type is CorrelationType.ATTACK_CHAIN
    assert correlation.findings == (finding_id,)


def test_correlation_rejects_without_proof() -> None:
    with pytest.raises(ValueError):
        Correlation(
            correlation_id=CorrelationId("cor_0002"),
            type=CorrelationType.EXPOSURE,
            assets=(AssetId("ast_0001"),),
            findings=(),
            impact=ImpactScore(value=0.5),
            reason="No evidence.",
        )


def test_correlation_rejects_empty_reason() -> None:
    with pytest.raises(ValueError):
        Correlation(
            correlation_id=CorrelationId("cor_0003"),
            type=CorrelationType.TEMPORAL,
            assets=(),
            findings=(FindingId("fnd_0002"),),
            impact=ImpactScore(value=0.4),
            reason="",
        )
