"""Tests for the IdentityRisk inventory aggregate (context: identity_risk, SEC-19)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.identity_risk.access_risk import AccessRisk
from hexa_sec.domain.identity_risk.identity_finding import IdentityFinding
from hexa_sec.domain.identity_risk.identity_risk import IdentityRisk
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


def test_for_principal_consolidates_findings() -> None:
    findings = (
        _finding(issue="orphan_account"),
        _finding(issue="excessive_rights", access_risk=AccessRisk.EXCESSIVE),
        _finding(issue="privileged_access", access_risk=AccessRisk.PRIVILEGED),
    )
    risk = IdentityRisk.for_principal("svc-backup", findings)
    assert risk.principal == "svc-backup"
    assert len(risk.findings) == 3
    assert risk.risk_count == 3
    assert risk.privileged_count == 1


def test_for_principal_deduplicates_identical_findings() -> None:
    findings = (_finding(), _finding())
    risk = IdentityRisk.for_principal("svc-backup", findings)
    assert len(risk.findings) == 1


def test_for_principal_dedup_normalizes_padded_issue() -> None:
    findings = (
        _finding(issue="orphan_account", evidence="a"),
        _finding(issue="orphan_account  ", evidence="b"),
    )
    risk = IdentityRisk.for_principal("svc-backup", findings)
    assert len(risk.findings) == 1


def test_for_principal_keeps_distinct_issues_separate() -> None:
    findings = (
        _finding(issue="orphan_account", evidence="a"),
        _finding(issue="excessive_rights", evidence="b"),
    )
    risk = IdentityRisk.for_principal("svc-backup", findings)
    assert len(risk.findings) == 2


def test_for_principal_keeps_technical_account() -> None:
    technical = _finding(access_risk=AccessRisk.SERVICE, severity=Severity.LOW)
    risk = IdentityRisk.for_principal("svc-backup", (technical,))
    assert len(risk.findings) == 1
    assert risk.findings[0].access_risk is AccessRisk.SERVICE


def test_for_principal_ignores_other_principal() -> None:
    risk = IdentityRisk.for_principal("svc-backup", (_finding(principal="admin"),))
    assert risk.findings == ()
    assert risk.risk_count == 0


def test_for_principal_rejects_blank_principal() -> None:
    with pytest.raises(ValueError):
        IdentityRisk.for_principal("   ", ())


def test_for_principal_no_findings_returns_empty() -> None:
    risk = IdentityRisk.for_principal("svc-backup", ())
    assert risk.findings == ()
    assert risk.risk_count == 0
    assert risk.privileged_count == 0


def test_for_principal_privileged_count() -> None:
    findings = (
        _finding(issue="a", access_risk=AccessRisk.PRIVILEGED),
        _finding(issue="b", access_risk=AccessRisk.ORPHAN),
        _finding(issue="c", access_risk=AccessRisk.SERVICE),
    )
    risk = IdentityRisk.for_principal("svc-backup", findings)
    assert risk.privileged_count == 1
    assert risk.risk_count == 3


def test_for_principal_is_deterministic() -> None:
    findings = (
        _finding(issue="a", access_risk=AccessRisk.PRIVILEGED),
        _finding(issue="b", access_risk=AccessRisk.ORPHAN, severity=Severity.MEDIUM),
    )
    first = IdentityRisk.for_principal("svc-backup", findings)
    second = IdentityRisk.for_principal("svc-backup", findings)
    assert first == second
    assert first.privileged_count == second.privileged_count


# --- Category: concurrence / ordre (dedup max-sévérité, indépendant de l'ordre) ---


def test_for_principal_dedup_keeps_highest_severity() -> None:
    first = _finding(issue="orphan_account", severity=Severity.MEDIUM, evidence="a")
    second = _finding(issue="orphan_account", severity=Severity.CRITICAL, evidence="b")
    risk = IdentityRisk.for_principal("svc-backup", (first, second))
    assert len(risk.findings) == 1
    assert risk.findings[0].severity is Severity.CRITICAL


def test_for_principal_dedup_order_independent_for_severity() -> None:
    medium = _finding(issue="orphan_account", severity=Severity.MEDIUM, evidence="a")
    critical = _finding(issue="orphan_account", severity=Severity.CRITICAL, evidence="b")
    first = IdentityRisk.for_principal("svc-backup", (medium, critical))
    second = IdentityRisk.for_principal("svc-backup", (critical, medium))
    assert first == second
    assert first.findings[0].severity is Severity.CRITICAL


# --- Category: stabilité / déterminisme (tie-break sur evidence) ------------


def test_for_principal_dedup_same_severity_keeps_smallest_evidence() -> None:
    a = _finding(severity=Severity.HIGH, evidence="zzz")
    b = _finding(severity=Severity.HIGH, evidence="aaa")
    risk = IdentityRisk.for_principal("svc-backup", (a, b))
    assert len(risk.findings) == 1
    assert risk.findings[0].evidence == "aaa"


def test_for_principal_dedup_order_independent_for_evidence() -> None:
    a = _finding(severity=Severity.HIGH, evidence="zzz")
    b = _finding(severity=Severity.HIGH, evidence="aaa")
    first = IdentityRisk.for_principal("svc-backup", (a, b))
    second = IdentityRisk.for_principal("svc-backup", (b, a))
    assert first == second
    assert first.findings[0].evidence == "aaa"


def test_for_principal_dedup_complex_is_order_independent() -> None:
    c_zzz = _finding(severity=Severity.CRITICAL, evidence="zzz")
    c_aaa = _finding(severity=Severity.CRITICAL, evidence="aaa")
    h_bbb = _finding(severity=Severity.HIGH, evidence="bbb")
    evidences = {
        IdentityRisk.for_principal("svc-backup", permutation).findings[0].evidence
        for permutation in _permutations((c_zzz, c_aaa, h_bbb))
    }
    assert evidences == {"aaa"}


def _permutations(values: tuple[IdentityFinding, ...]) -> list[tuple[IdentityFinding, ...]]:
    if len(values) <= 1:
        return [values]
    out: list[tuple[IdentityFinding, ...]] = []
    for index in range(len(values)):
        rest = values[:index] + values[index + 1 :]
        for tail in _permutations(rest):
            out.append((values[index],) + tail)
    return out
