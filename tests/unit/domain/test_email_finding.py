"""Tests for EmailFinding (context: email_risk)."""

from __future__ import annotations

from hexa_sec.domain.email_risk.dmarc_status import DmarcStatus
from hexa_sec.domain.email_risk.email_finding import EmailFinding
from hexa_sec.domain.email_risk.email_record import EmailRecord


def test_email_finding_spoofable_when_dmarc_missing() -> None:
    finding = EmailFinding(
        record=EmailRecord(domain="acme.example"), dmarc=DmarcStatus.MISSING
    )
    assert finding.spoofable() is True


def test_email_finding_not_spoofable_when_reject() -> None:
    finding = EmailFinding(
        record=EmailRecord(domain="acme.example"), dmarc=DmarcStatus.REJECT
    )
    assert finding.spoofable() is False


def test_email_finding_exposes_domain() -> None:
    finding = EmailFinding(record=EmailRecord(domain="acme.example"), dmarc=DmarcStatus.NONE)
    assert finding.domain == "acme.example"
