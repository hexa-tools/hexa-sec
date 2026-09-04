"""Tests for the EmailRisk aggregate (context: email_risk)."""

from __future__ import annotations

from hexa_sec.domain.email_risk.dmarc_status import DmarcStatus
from hexa_sec.domain.email_risk.email_finding import EmailFinding
from hexa_sec.domain.email_risk.email_record import EmailRecord
from hexa_sec.domain.email_risk.email_risk import EmailRisk


def _finding(domain: str, dmarc: DmarcStatus) -> EmailFinding:
    return EmailFinding(record=EmailRecord(domain=domain), dmarc=dmarc)


def test_of_consolidates_findings() -> None:
    findings = (
        _finding("acme.example", DmarcStatus.MISSING),
        _finding("corp.example", DmarcStatus.REJECT),
    )
    risk = EmailRisk.of(findings)
    assert len(risk.findings) == 2
    assert risk.spoofable_count == 1


def test_of_deduplicates_same_domain() -> None:
    findings = (
        _finding("acme.example", DmarcStatus.NONE),
        _finding("acme.example", DmarcStatus.REJECT),
    )
    risk = EmailRisk.of(findings)
    assert len(risk.findings) == 1


def test_of_keeps_worst_dmarc() -> None:
    findings = (
        _finding("acme.example", DmarcStatus.REJECT),
        _finding("acme.example", DmarcStatus.NONE),
    )
    risk = EmailRisk.of(findings)
    assert risk.findings[0].dmarc is DmarcStatus.NONE
    assert risk.findings[0].spoofable() is True


def test_of_keeps_worst_dmarc_missing_over_none() -> None:
    missing = _finding("acme.example", DmarcStatus.MISSING)
    none = _finding("acme.example", DmarcStatus.NONE)
    assert EmailRisk.of((missing, none)).findings[0].dmarc is DmarcStatus.MISSING
    assert EmailRisk.of((none, missing)).findings[0].dmarc is DmarcStatus.MISSING


def test_of_keeps_worst_dmarc_none_over_quarantine() -> None:
    none = _finding("acme.example", DmarcStatus.NONE)
    quarantine = _finding("acme.example", DmarcStatus.QUARANTINE)
    assert EmailRisk.of((none, quarantine)).findings[0].dmarc is DmarcStatus.NONE
    assert EmailRisk.of((quarantine, none)).findings[0].dmarc is DmarcStatus.NONE


def test_of_keeps_worst_dmarc_quarantine_over_reject() -> None:
    quarantine = _finding("acme.example", DmarcStatus.QUARANTINE)
    reject = _finding("acme.example", DmarcStatus.REJECT)
    assert EmailRisk.of((quarantine, reject)).findings[0].dmarc is DmarcStatus.QUARANTINE
    assert EmailRisk.of((reject, quarantine)).findings[0].dmarc is DmarcStatus.QUARANTINE


def test_of_spoofable_domains() -> None:
    findings = (
        _finding("acme.example", DmarcStatus.MISSING),
        _finding("corp.example", DmarcStatus.REJECT),
    )
    risk = EmailRisk.of(findings)
    assert risk.spoofable_domains() == ("acme.example",)
    assert risk.spoofable_count == 1


def test_of_empty_is_empty() -> None:
    risk = EmailRisk.of(())
    assert risk.findings == ()
    assert risk.spoofable_count == 0
    assert risk.spoofable_domains() == ()


def test_of_is_deterministic() -> None:
    findings = (
        _finding("acme.example", DmarcStatus.MISSING),
        _finding("corp.example", DmarcStatus.REJECT),
    )
    first = EmailRisk.of(findings)
    second = EmailRisk.of(findings)
    assert first == second
    assert first.spoofable_count == second.spoofable_count


def test_of_order_independent() -> None:
    a = _finding("acme.example", DmarcStatus.MISSING)
    b = _finding("corp.example", DmarcStatus.REJECT)
    first = EmailRisk.of((a, b))
    second = EmailRisk.of((b, a))
    assert first == second
    assert [finding.domain for finding in first.findings] == [
        finding.domain for finding in second.findings
    ]
