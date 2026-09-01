"""Tests for the ContainerRisk aggregate (context: container_risk)."""

from __future__ import annotations

from hexa_sec.domain.container_risk.container_finding import ContainerFinding
from hexa_sec.domain.container_risk.container_risk import ContainerRisk
from hexa_sec.domain.container_risk.image_ref import ImageRef
from hexa_sec.domain.finding.severity import Severity


def _finding(image: str, cve: str, severity: Severity = Severity.CRITICAL) -> ContainerFinding:
    return ContainerFinding(image=ImageRef(image, "1.4.2"), cve=cve, severity=severity)


def test_of_consolidates_findings() -> None:
    findings = (
        _finding("acme/payment", "CVE-2024-3094"),
        _finding("acme/orders", "CVE-2024-0001", severity=Severity.MEDIUM),
    )
    risk = ContainerRisk.of(findings)
    assert len(risk.findings) == 2
    assert risk.vulnerable_count == 2
    assert risk.severe_count == 1


def test_of_deduplicates_same_image_cve() -> None:
    findings = (
        _finding("acme/payment", "CVE-2024-3094"),
        _finding("acme/payment", "CVE-2024-3094"),
    )
    risk = ContainerRisk.of(findings)
    assert len(risk.findings) == 1


def test_of_keeps_higher_severity() -> None:
    findings = (
        _finding("acme/payment", "CVE-2024-3094", severity=Severity.HIGH),
        _finding("acme/payment", "CVE-2024-3094", severity=Severity.CRITICAL),
    )
    risk = ContainerRisk.of(findings)
    assert len(risk.findings) == 1
    assert risk.findings[0].severity is Severity.CRITICAL


def test_of_same_cve_different_images_separate() -> None:
    findings = (
        _finding("acme/payment", "CVE-2024-3094"),
        _finding("acme/orders", "CVE-2024-3094"),
    )
    risk = ContainerRisk.of(findings)
    assert len(risk.findings) == 2


def test_of_severe_images() -> None:
    findings = (
        _finding("acme/payment", "CVE-2024-3094"),
        _finding("acme/orders", "CVE-2024-0001", severity=Severity.LOW),
    )
    risk = ContainerRisk.of(findings)
    assert risk.severe_images() == ("acme/payment:1.4.2",)
    assert risk.severe_count == 1


def test_of_empty_is_empty() -> None:
    risk = ContainerRisk.of(())
    assert risk.findings == ()
    assert risk.vulnerable_count == 0
    assert risk.severe_count == 0


def test_of_is_deterministic() -> None:
    findings = (
        _finding("acme/payment", "CVE-2024-3094"),
        _finding("acme/orders", "CVE-2024-0001", severity=Severity.MEDIUM),
    )
    first = ContainerRisk.of(findings)
    second = ContainerRisk.of(findings)
    assert first == second
    assert first.severe_count == second.severe_count


def test_of_order_independent() -> None:
    a = _finding("acme/payment", "CVE-2024-3094")
    b = _finding("acme/orders", "CVE-2024-0001", severity=Severity.MEDIUM)
    first = ContainerRisk.of((a, b))
    second = ContainerRisk.of((b, a))
    assert first == second
    assert [f.image.qualified for f in first.findings] == [
        f.image.qualified for f in second.findings
    ]
