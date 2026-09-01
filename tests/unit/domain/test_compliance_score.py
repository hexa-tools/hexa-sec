"""Tests for ComplianceScore (context: compliance)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.compliance.compliance_score import ComplianceLevel, ComplianceScore
from hexa_sec.domain.compliance.compliance_scope import ComplianceScope


def test_compliance_score_creation() -> None:
    score = ComplianceScore(scope=ComplianceScope.ISO_27001, value=72)
    assert score.value == 72
    assert score.level() is ComplianceLevel.ADEQUATE


def test_compliance_score_rejects_out_of_range() -> None:
    with pytest.raises(ValueError):
        ComplianceScore(scope=ComplianceScope.RGPD, value=101)
    with pytest.raises(ValueError):
        ComplianceScore(scope=ComplianceScope.RGPD, value=-1)


def test_compliance_score_levels() -> None:
    assert (
        ComplianceScore(scope=ComplianceScope.PCI_DSS, value=95).level()
        is ComplianceLevel.COMPLIANT
    )
    assert (
        ComplianceScore(scope=ComplianceScope.PCI_DSS, value=40).level()
        is ComplianceLevel.NON_COMPLIANT
    )


def test_compliance_score_accepts_bounds() -> None:
    assert ComplianceScore(scope=ComplianceScope.ISO_27001, value=0).value == 0
    assert ComplianceScore(scope=ComplianceScope.ISO_27001, value=100).value == 100


def test_compliance_score_threshold_boundaries() -> None:
    assert (
        ComplianceScore(scope=ComplianceScope.RGPD, value=85).level() is ComplianceLevel.COMPLIANT
    )
    assert ComplianceScore(scope=ComplianceScope.RGPD, value=84).level() is ComplianceLevel.ADEQUATE
    assert ComplianceScore(scope=ComplianceScope.RGPD, value=60).level() is ComplianceLevel.ADEQUATE
    assert (
        ComplianceScore(scope=ComplianceScope.RGPD, value=59).level()
        is ComplianceLevel.NON_COMPLIANT
    )
