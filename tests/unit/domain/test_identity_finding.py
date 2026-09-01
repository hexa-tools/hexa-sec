"""Tests for IdentityFinding (context: identity_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.identity_risk.identity_finding import IdentityFinding


def test_identity_finding_creation() -> None:
    finding = IdentityFinding(principal="svc-backup", issue="orphan_account")
    assert finding.issue == "orphan_account"


def test_identity_finding_rejects_empty_principal() -> None:
    with pytest.raises(ValueError):
        IdentityFinding(principal="", issue="orphan_account")


def test_identity_finding_rejects_empty_issue() -> None:
    with pytest.raises(ValueError):
        IdentityFinding(principal="svc-backup", issue="")
