"""Tests for ComplianceScope (context: compliance)."""

from __future__ import annotations

from hexa_sec.domain.compliance.compliance_scope import ComplianceScope


def test_compliance_scope_members() -> None:
    assert ComplianceScope.ISO_27001.value == "iso_27001"
    assert ComplianceScope.RGPD.value == "rgpd"
    assert ComplianceScope.NIS2.value == "nis2"
    assert ComplianceScope.PCI_DSS.value == "pci_dss"


def test_compliance_scope_is_unique() -> None:
    values = [member.value for member in ComplianceScope]
    assert len(values) == len(set(values))
