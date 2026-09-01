"""Tests for Remediation (context: remediation)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.remediation.remediation import Remediation
from hexa_sec.domain.remediation.remediation_status import RemediationStatus


def test_remediation_creation() -> None:
    remediation = Remediation(finding_id="fnd_0001", instruction="Upgrade to 1.2.0")
    assert remediation.status is RemediationStatus.OPEN


def test_remediation_rejects_empty_instruction() -> None:
    with pytest.raises(ValueError):
        Remediation(finding_id="fnd_0001", instruction="")
