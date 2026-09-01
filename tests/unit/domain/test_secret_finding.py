"""Tests for SecretFinding (context: secret_risk, SEC-12)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.secret_risk.secret_finding import SecretFinding
from hexa_sec.domain.secret_risk.secret_type import SecretType


def _finding(
    asset: str = "acme/api",
    secret_type: SecretType = SecretType.TOKEN,
    evidence: str = ".env:13: JWT_auth",
    revoked: bool = False,
) -> SecretFinding:
    return SecretFinding(
        asset=asset,
        secret_type=secret_type,
        evidence=evidence,
        revoked=revoked,
    )


def test_secret_finding_creation() -> None:
    finding = _finding()
    assert finding.asset == "acme/api"
    assert finding.secret_type is SecretType.TOKEN
    assert finding.evidence == ".env:13: JWT_auth"
    assert finding.revoked is False


def test_secret_finding_rejects_empty_asset() -> None:
    with pytest.raises(ValueError):
        _finding(asset="")


def test_secret_finding_rejects_whitespace_asset() -> None:
    with pytest.raises(ValueError):
        _finding(asset="   ")


def test_secret_finding_rejects_empty_evidence() -> None:
    with pytest.raises(ValueError):
        _finding(evidence="")


def test_secret_finding_rejects_blank_evidence() -> None:
    with pytest.raises(ValueError):
        _finding(evidence="   ")


def test_secret_finding_rejects_non_secret_type() -> None:
    with pytest.raises(ValueError):
        SecretFinding(
            asset="acme/api",
            secret_type="token",
            evidence=".env:13: JWT_auth",
        )


def test_secret_finding_severity_follows_type() -> None:
    assert _finding(secret_type=SecretType.PRIVATEKEY).severity.level is Severity.CRITICAL
    assert _finding(secret_type=SecretType.CIPHERTEXT).severity.level is Severity.LOW
