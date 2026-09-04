"""Tests for the ComplianceRisk aggregate (context: compliance, SEC-18)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.compliance.compliance_finding import ComplianceFinding
from hexa_sec.domain.compliance.compliance_risk import ComplianceRisk
from hexa_sec.domain.compliance.compliance_scope import ComplianceScope
from hexa_sec.domain.finding.finding import FindingId
from hexa_sec.domain.finding.severity import Severity


def _gap(
    finding_id: str = "f-42",
    scope: ComplianceScope = ComplianceScope.ISO_27001,
    impact: Severity = Severity.HIGH,
) -> ComplianceFinding:
    return ComplianceFinding(
        finding_id=FindingId(finding_id),
        scope=scope,
        impact=impact,
    )


def test_for_asset_consolidates_gaps_by_scope() -> None:
    gaps = (
        _gap(finding_id="f-1", scope=ComplianceScope.ISO_27001),
        _gap(finding_id="f-2", scope=ComplianceScope.NIS2, impact=Severity.CRITICAL),
    )
    risk = ComplianceRisk.for_asset("acme", gaps)
    assert risk.asset == "acme"
    assert len(risk.gaps) == 2
    assert {g.scope for g in risk.gaps} == {ComplianceScope.ISO_27001, ComplianceScope.NIS2}


def test_for_asset_deduplicates_same_finding_scope() -> None:
    gaps = (_gap(finding_id="f-1"), _gap(finding_id="f-1"))
    risk = ComplianceRisk.for_asset("acme", gaps)
    assert len(risk.gaps) == 1


def test_for_asset_dedup_keeps_higher_impact() -> None:
    gaps = (
        _gap(finding_id="f-1", impact=Severity.MEDIUM),
        _gap(finding_id="f-1", impact=Severity.CRITICAL),
    )
    risk = ComplianceRisk.for_asset("acme", gaps)
    assert len(risk.gaps) == 1
    assert risk.gaps[0].impact is Severity.CRITICAL


def test_for_asset_dedup_keeps_higher_impact_order_independent() -> None:
    medium = _gap(finding_id="f-1", impact=Severity.MEDIUM)
    critical = _gap(finding_id="f-1", impact=Severity.CRITICAL)
    first = ComplianceRisk.for_asset("acme", (critical, medium))
    second = ComplianceRisk.for_asset("acme", (medium, critical))
    assert first.gaps[0].impact is Severity.CRITICAL
    assert second.gaps[0].impact is Severity.CRITICAL


def test_for_asset_scores_empty_scope_maximal() -> None:
    risk = ComplianceRisk.for_asset("acme", ())
    iso = next(s for s in risk.scores if s.scope is ComplianceScope.ISO_27001)
    assert iso.value == 100
    assert iso.level().value == "compliant"


def test_for_asset_reduces_score_by_gap_impact() -> None:
    gaps = (_gap(finding_id="f-1", scope=ComplianceScope.ISO_27001, impact=Severity.CRITICAL),)
    risk = ComplianceRisk.for_asset("acme", gaps)
    iso = next(s for s in risk.scores if s.scope is ComplianceScope.ISO_27001)
    assert iso.value == 68


def test_for_asset_clamps_score_at_zero() -> None:
    gaps = tuple(
        _gap(finding_id=f"{i}", scope=ComplianceScope.RGPD, impact=Severity.CRITICAL)
        for i in range(5)
    )
    risk = ComplianceRisk.for_asset("acme", gaps)
    rgpd = next(s for s in risk.scores if s.scope is ComplianceScope.RGPD)
    assert rgpd.value == 0


def test_for_asset_non_compliant_scopes() -> None:
    gaps = (
        _gap(finding_id="f-1", scope=ComplianceScope.PCI_DSS, impact=Severity.CRITICAL),
        _gap(finding_id="f-2", scope=ComplianceScope.PCI_DSS, impact=Severity.CRITICAL),
    )
    risk = ComplianceRisk.for_asset("acme", gaps)
    assert ComplianceScope.PCI_DSS in risk.non_compliant_scopes()


def test_for_asset_rejects_blank_asset() -> None:
    with pytest.raises(ValueError):
        ComplianceRisk.for_asset("   ", ())


def test_for_asset_scores_all_scopes_base_traced() -> None:
    risk = ComplianceRisk.for_asset("acme", ())
    assert {s.scope for s in risk.scores} == set(ComplianceScope)


def test_for_asset_score_levels_coherent() -> None:
    gaps = (_gap(finding_id="f-1", scope=ComplianceScope.PCI_DSS, impact=Severity.CRITICAL),)
    risk = ComplianceRisk.for_asset("acme", gaps)
    for score in risk.scores:
        assert score.level().value == (
            "compliant"
            if score.value >= 85
            else "adequate"
            if score.value >= 60
            else "non_compliant"
        )


def test_for_asset_normalizes_asset() -> None:
    risk = ComplianceRisk.for_asset("  acme  ", ())
    assert risk.asset == "acme"


def test_for_asset_is_deterministic() -> None:
    gaps = (
        _gap(finding_id="f-1", scope=ComplianceScope.ISO_27001),
        _gap(finding_id="f-2", scope=ComplianceScope.RGPD, impact=Severity.CRITICAL),
    )
    first = ComplianceRisk.for_asset("acme", gaps)
    second = ComplianceRisk.for_asset("acme", gaps)
    assert first == second
    assert first.scores == second.scores


def test_for_asset_order_independent_gaps() -> None:
    a = _gap(finding_id="f-1", scope=ComplianceScope.ISO_27001)
    b = _gap(finding_id="f-2", scope=ComplianceScope.RGPD)
    first = ComplianceRisk.for_asset("acme", (a, b))
    second = ComplianceRisk.for_asset("acme", (b, a))
    assert first == second
    assert [g.finding_id.value for g in first.gaps] == [g.finding_id.value for g in second.gaps]
