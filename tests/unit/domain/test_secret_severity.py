"""Tests for the SecretSeverity value object (context: secret_risk, SEC-12)."""

from __future__ import annotations

from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.secret_risk.secret_severity import SecretSeverity
from hexa_sec.domain.secret_risk.secret_type import SecretType


def test_secret_severity_for_sensitive_types_is_critical() -> None:
    for secret_type in (SecretType.PRIVATEKEY, SecretType.AWSKEY, SecretType.PASSWORD):
        severity = SecretSeverity.for_type(secret_type)
        assert severity.level is Severity.CRITICAL
        assert severity.sensitive is True
        assert severity.is_critical is True


def test_secret_severity_for_tokens_and_api_is_high() -> None:
    for secret_type in (SecretType.TOKEN, SecretType.APIKEY):
        severity = SecretSeverity.for_type(secret_type)
        assert severity.level is Severity.HIGH
        assert severity.sensitive is True
        assert severity.is_critical is False


def test_secret_severity_for_banal_type_is_low() -> None:
    severity = SecretSeverity.for_type(SecretType.CIPHERTEXT)
    assert severity.level is Severity.LOW
    assert severity.sensitive is False
    assert severity.is_critical is False


def test_secret_severity_never_critical_by_default() -> None:
    banal = SecretSeverity.for_type(SecretType.CIPHERTEXT)
    assert banal.level is not Severity.CRITICAL
