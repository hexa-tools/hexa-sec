"""Tests for DmarcStatus (context: email_risk)."""

from __future__ import annotations

from hexa_sec.domain.email_risk.dmarc_status import DmarcStatus


def test_dmarc_status_values() -> None:
    assert DmarcStatus.REJECT.value == "reject"
    assert DmarcStatus.MISSING.value == "missing"


def test_dmarc_status_enforced() -> None:
    assert DmarcStatus.REJECT.enforced is True
    assert DmarcStatus.QUARANTINE.enforced is True
    assert DmarcStatus.NONE.enforced is False
    assert DmarcStatus.MISSING.enforced is False
