"""Tests for ComplianceFinding (context: compliance, SEC-18)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.compliance.compliance_finding import ComplianceFinding
from hexa_sec.domain.compliance.compliance_scope import ComplianceScope
from hexa_sec.domain.finding.finding import FindingId
from hexa_sec.domain.finding.severity import Severity


def _finding(
    finding_id: FindingId = FindingId("f-42"),
    scope: ComplianceScope = ComplianceScope.ISO_27001,
    impact: Severity = Severity.HIGH,
) -> ComplianceFinding:
    return ComplianceFinding(
        finding_id=finding_id,
        scope=scope,
        impact=impact,
    )


def test_compliance_finding_creation() -> None:
    finding = _finding()
    assert finding.finding_id == FindingId("f-42")
    assert finding.scope is ComplianceScope.ISO_27001
    assert finding.impact is Severity.HIGH


def test_compliance_finding_rejects_blank_finding_id() -> None:
    with pytest.raises(ValueError):
        _finding(finding_id=FindingId(""))


def test_compliance_finding_rejects_whitespace_finding_id() -> None:
    with pytest.raises(ValueError):
        _finding(finding_id=FindingId("   "))


def test_compliance_finding_rejects_non_scope() -> None:
    with pytest.raises(ValueError):
        ComplianceFinding(
            finding_id=FindingId("f-42"),
            scope="iso_27001",
            impact=Severity.HIGH,
        )


def test_compliance_finding_rejects_non_severity() -> None:
    with pytest.raises(ValueError):
        ComplianceFinding(
            finding_id=FindingId("f-42"),
            scope=ComplianceScope.ISO_27001,
            impact="high",
        )
