"""Tests for SecretFinding (context: secret_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.secret_risk.secret_finding import SecretFinding
from hexa_sec.domain.secret_risk.secret_type import SecretType


def test_secret_finding_creation() -> None:
    finding = SecretFinding(path="src/.env", kind=SecretType.API_KEY)
    assert finding.kind is SecretType.API_KEY


def test_secret_finding_rejects_empty_path() -> None:
    with pytest.raises(ValueError):
        SecretFinding(path="", kind=SecretType.API_KEY)
