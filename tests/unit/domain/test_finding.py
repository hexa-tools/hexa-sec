"""Tests for FindingId + Finding (context: finding)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.finding.confidence import Confidence
from hexa_sec.domain.finding.finding import Finding, FindingId
from hexa_sec.domain.finding.severity import Severity


def test_finding_creation() -> None:
    finding = Finding(
        finding_id=FindingId("fnd_0001"),
        title="SQL injection on login",
        severity=Severity.HIGH,
        confidence=Confidence.CERTAIN,
    )
    assert finding.title == "SQL injection on login"
    assert finding.severity is Severity.HIGH
    assert finding.confidence is Confidence.CERTAIN


def test_finding_defaults() -> None:
    finding = Finding(finding_id=FindingId("fnd_0002"), title="Open port")
    assert finding.severity is Severity.MEDIUM
    assert finding.confidence is Confidence.MEDIUM


def test_finding_rejects_empty_title() -> None:
    with pytest.raises(ValueError):
        Finding(finding_id=FindingId("fnd_0003"), title="")


def test_finding_is_critical_predicate() -> None:
    critical = Finding(finding_id=FindingId("fnd_0001"), title="x", severity=Severity.CRITICAL)
    assert critical.is_critical() is True
    assert _not_critical().is_critical() is False


def _not_critical() -> Finding:
    return Finding(finding_id=FindingId("fnd_0002"), title="x", severity=Severity.LOW)


def test_finding_equality_by_value() -> None:
    first = Finding(finding_id=FindingId("fnd_0004"), title="XSS")
    second = Finding(finding_id=FindingId("fnd_0004"), title="XSS")
    assert first == second
