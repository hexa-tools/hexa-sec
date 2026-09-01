"""Tests for the IaacRisk inventory aggregate (context: iaac_risk, SEC-17)."""

from __future__ import annotations

from hexa_sec.domain.iaac_risk.ia_c_file_name import IaCFileName
from hexa_sec.domain.iaac_risk.iaac_finding import IaacFinding
from hexa_sec.domain.iaac_risk.iaac_risk import IaacRisk
from hexa_sec.domain.iaac_risk.resource_type import ResourceType
from hexa_sec.domain.finding.severity import Severity


def _finding(
    resource_type: ResourceType = ResourceType.AWS_S3_BUCKET,
    path: str = "infra/main.tf",
    severity: Severity = Severity.HIGH,
    evidence: str = "bucket ACL public",
) -> IaacFinding:
    return IaacFinding(
        resource_type=resource_type,
        path=IaCFileName(path),
        severity=severity,
        evidence=evidence,
    )


def test_for_asset_consolidates_findings() -> None:
    findings = (
        _finding(path="infra/main.tf"),
        _finding(resource_type=ResourceType.AWS_SECURITY_GROUP, path="infra/net.tf"),
        _finding(
            resource_type=ResourceType.TERRAFORM, path="infra/other.tf", severity=Severity.LOW
        ),
    )
    risk = IaacRisk.for_asset("acme/infra", findings)
    assert risk.asset == "acme/infra"
    assert len(risk.findings) == 3
    assert risk.risk_count == 3
    assert risk.critical_count == 0


def test_for_asset_deduplicates_identical_findings() -> None:
    findings = (_finding(), _finding())
    risk = IaacRisk.for_asset("acme/infra", findings)
    assert len(risk.findings) == 1


def test_for_asset_keeps_distinct_resources_separate() -> None:
    findings = (
        _finding(path="infra/a.tf", evidence="a"),
        _finding(path="infra/b.tf", evidence="b"),
    )
    risk = IaacRisk.for_asset("acme/infra", findings)
    assert len(risk.findings) == 2


def test_for_asset_keeps_low_severity_generic() -> None:
    generic = _finding(resource_type=ResourceType.TERRAFORM, severity=Severity.LOW)
    risk = IaacRisk.for_asset("acme/infra", (generic,))
    assert len(risk.findings) == 1
    assert risk.findings[0].severity is Severity.LOW


def test_for_asset_no_findings_returns_empty() -> None:
    risk = IaacRisk.for_asset("acme/infra", ())
    assert risk.findings == ()
    assert risk.risk_count == 0
    assert risk.critical_count == 0


def test_for_asset_critical_count_only_critical() -> None:
    findings = (
        _finding(path="infra/a.tf", severity=Severity.CRITICAL),
        _finding(resource_type=ResourceType.TERRAFORM, path="infra/b.tf", severity=Severity.MEDIUM),
        _finding(resource_type=ResourceType.TERRAFORM, path="infra/c.tf", severity=Severity.LOW),
    )
    risk = IaacRisk.for_asset("acme/infra", findings)
    assert risk.critical_count == 1
    assert risk.risk_count == 3


def test_for_asset_is_deterministic() -> None:
    findings = (
        _finding(path="infra/a.tf", severity=Severity.CRITICAL),
        _finding(resource_type=ResourceType.TERRAFORM, path="infra/b.tf", severity=Severity.MEDIUM),
    )
    first = IaacRisk.for_asset("acme/infra", findings)
    second = IaacRisk.for_asset("acme/infra", findings)
    assert first == second
    assert first.critical_count == second.critical_count


# --- Category: concurrence / ordre (dedup max-sévérité, indépendant de l'ordre) ---


def test_for_asset_dedup_keeps_highest_severity() -> None:
    first = _finding(resource_type=ResourceType.TERRAFORM, severity=Severity.MEDIUM, evidence="a")
    second = _finding(
        resource_type=ResourceType.TERRAFORM, severity=Severity.CRITICAL, evidence="b"
    )
    risk = IaacRisk.for_asset("acme/infra", (first, second))
    assert len(risk.findings) == 1
    assert risk.findings[0].severity is Severity.CRITICAL


def test_for_asset_dedup_order_independent_for_severity() -> None:
    medium = _finding(resource_type=ResourceType.TERRAFORM, severity=Severity.MEDIUM, evidence="a")
    critical = _finding(
        resource_type=ResourceType.TERRAFORM, severity=Severity.CRITICAL, evidence="b"
    )
    first = IaacRisk.for_asset("acme/infra", (medium, critical))
    second = IaacRisk.for_asset("acme/infra", (critical, medium))
    assert first == second
    assert first.findings[0].severity is Severity.CRITICAL


# --- Category: stabilité / déterminisme (tie-break sur evidence) ------------


def test_for_asset_dedup_same_severity_keeps_smallest_evidence() -> None:
    a = _finding(severity=Severity.HIGH, evidence="zzz")
    b = _finding(severity=Severity.HIGH, evidence="aaa")
    risk = IaacRisk.for_asset("acme/infra", (a, b))
    assert len(risk.findings) == 1
    assert risk.findings[0].evidence == "aaa"


def test_for_asset_dedup_order_independent_for_evidence() -> None:
    a = _finding(severity=Severity.HIGH, evidence="zzz")
    b = _finding(severity=Severity.HIGH, evidence="aaa")
    first = IaacRisk.for_asset("acme/infra", (a, b))
    second = IaacRisk.for_asset("acme/infra", (b, a))
    assert first == second
    assert first.findings[0].evidence == "aaa"


def test_for_asset_dedup_complex_is_order_independent() -> None:
    c_zzz = _finding(severity=Severity.CRITICAL, evidence="zzz")
    c_aaa = _finding(severity=Severity.CRITICAL, evidence="aaa")
    h_bbb = _finding(severity=Severity.HIGH, evidence="bbb")
    evidences = {
        IaacRisk.for_asset("acme/infra", permutation).findings[0].evidence
        for permutation in _permutations((c_zzz, c_aaa, h_bbb))
    }
    assert evidences == {"aaa"}


def _permutations(values: tuple[IaacFinding, ...]) -> list[tuple[IaacFinding, ...]]:
    if len(values) <= 1:
        return [values]
    out: list[tuple[IaacFinding, ...]] = []
    for index in range(len(values)):
        rest = values[:index] + values[index + 1 :]
        for tail in _permutations(rest):
            out.append((values[index],) + tail)
    return out
