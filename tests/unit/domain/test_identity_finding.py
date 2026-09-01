"""Tests for IdentityFinding (context: identity_risk, SEC-19)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.identity_risk.access_risk import AccessRisk
from hexa_sec.domain.identity_risk.identity_finding import IdentityFinding
from hexa_sec.domain.identity_risk.principal import Principal


def _finding(
    principal: str = "svc-backup",
    issue: str = "orphan_account",
    access_risk: AccessRisk = AccessRisk.ORPHAN,
    severity: Severity = Severity.HIGH,
    evidence: str = "no manager, unused 90d",
) -> IdentityFinding:
    return IdentityFinding(
        principal=Principal(principal),
        issue=issue,
        access_risk=access_risk,
        severity=severity,
        evidence=evidence,
    )


def test_identity_finding_creation() -> None:
    finding = _finding()
    assert finding.principal == Principal("svc-backup")
    assert finding.issue == "orphan_account"
    assert finding.access_risk is AccessRisk.ORPHAN
    assert finding.severity is Severity.HIGH
    assert finding.evidence == "no manager, unused 90d"


def test_identity_finding_rejects_non_principal() -> None:
    with pytest.raises(ValueError):
        IdentityFinding(
            principal="svc-backup",
            issue="orphan_account",
            access_risk=AccessRisk.ORPHAN,
            severity=Severity.HIGH,
            evidence="no manager",
        )


def test_identity_finding_rejects_empty_issue() -> None:
    with pytest.raises(ValueError):
        _finding(issue="")


def test_identity_finding_rejects_blank_issue() -> None:
    with pytest.raises(ValueError):
        _finding(issue="   ")


def test_identity_finding_normalizes_issue() -> None:
    assert _finding(issue="  orphan_account  ").issue == "orphan_account"


def test_identity_finding_rejects_non_access_risk() -> None:
    with pytest.raises(ValueError):
        IdentityFinding(
            principal=Principal("svc-backup"),
            issue="orphan_account",
            access_risk="orphan",
            severity=Severity.HIGH,
            evidence="no manager",
        )


def test_identity_finding_rejects_non_severity() -> None:
    with pytest.raises(ValueError):
        IdentityFinding(
            principal=Principal("svc-backup"),
            issue="orphan_account",
            access_risk=AccessRisk.ORPHAN,
            severity="high",
            evidence="no manager",
        )


def test_identity_finding_rejects_empty_evidence() -> None:
    with pytest.raises(ValueError):
        _finding(evidence="")


def test_identity_finding_rejects_blank_evidence() -> None:
    with pytest.raises(ValueError):
        _finding(evidence="   ")


def test_identity_finding_rejects_privileged_low() -> None:
    with pytest.raises(ValueError):
        _finding(access_risk=AccessRisk.PRIVILEGED, severity=Severity.LOW)


def test_identity_finding_accepts_privileged_high() -> None:
    assert (
        _finding(access_risk=AccessRisk.PRIVILEGED, severity=Severity.HIGH).severity
        is Severity.HIGH
    )
    assert (
        _finding(access_risk=AccessRisk.PRIVILEGED, severity=Severity.CRITICAL).severity
        is Severity.CRITICAL
    )


def test_identity_finding_accepts_technical_account_medium() -> None:
    assert (
        _finding(access_risk=AccessRisk.SERVICE, severity=Severity.MEDIUM).severity
        is Severity.MEDIUM
    )
