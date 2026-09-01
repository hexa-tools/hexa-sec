"""Tests for ContainerFinding (context: container_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.container_risk.container_finding import ContainerFinding
from hexa_sec.domain.container_risk.image_ref import ImageRef
from hexa_sec.domain.finding.severity import Severity


def test_container_finding_creation() -> None:
    finding = ContainerFinding(
        image=ImageRef("acme/payment", "1.4.2"), cve="CVE-2024-3094", severity=Severity.CRITICAL
    )
    assert finding.cve == "CVE-2024-3094"
    assert finding.severe() is True


def test_container_finding_default_severity() -> None:
    finding = ContainerFinding(image=ImageRef("acme/payment", "1.4.2"), cve="CVE-2024-3094")
    assert finding.severity is Severity.MEDIUM


def test_container_finding_not_severe_on_low() -> None:
    finding = ContainerFinding(
        image=ImageRef("acme/payment", "1.4.2"), cve="CVE-2024-3094", severity=Severity.LOW
    )
    assert finding.severe() is False


def test_container_finding_rejects_empty_cve() -> None:
    with pytest.raises(ValueError):
        ContainerFinding(image=ImageRef("acme/payment", "1.4.2"), cve="")
