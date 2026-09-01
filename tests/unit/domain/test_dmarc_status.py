"""Tests for DmarcStatus (context: email_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.email_risk.dmarc_status import DmarcStatus


def test_dmarc_status_values() -> None:
    assert DmarcStatus.REJECT.value == "reject"
    assert DmarcStatus.MISSING.value == "missing"


def test_dmarc_status_enforced() -> None:
    assert DmarcStatus.REJECT.enforced is True
    assert DmarcStatus.QUARANTINE.enforced is True
    assert DmarcStatus.NONE.enforced is False
    assert DmarcStatus.MISSING.enforced is False


def test_dmarc_status_normalize_accepts_known() -> None:
    assert DmarcStatus.normalize("none") is DmarcStatus.NONE
    assert DmarcStatus.normalize("REJECT") is DmarcStatus.REJECT
    assert DmarcStatus.normalize("quarantine") is DmarcStatus.QUARANTINE
    assert DmarcStatus.normalize("missing") is DmarcStatus.MISSING


def test_dmarc_status_normalize_accepts_policy_format() -> None:
    assert DmarcStatus.normalize("p=none") is DmarcStatus.NONE
    assert DmarcStatus.normalize("v=DMARC1; p=reject") is DmarcStatus.REJECT


def test_dmarc_status_normalize_rejects_unknown() -> None:
    with pytest.raises(ValueError):
        DmarcStatus.normalize("p=softfail")
    with pytest.raises(ValueError):
        DmarcStatus.normalize("v=DMARC1")


def test_dmarc_status_normalize_rejects_blank() -> None:
    with pytest.raises(ValueError):
        DmarcStatus.normalize("   ")
