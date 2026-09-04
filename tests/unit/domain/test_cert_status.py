"""Tests for the CertStatus enum (context: tls_risk, SEC-16)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.tls_risk.cert_status import CertStatus


def test_cert_status_members() -> None:
    assert CertStatus.OK.value == "ok"
    assert CertStatus.EXPIRED.value == "expired"
    assert CertStatus.EXPIRING.value == "expiring"
    assert CertStatus.INVALIDCHAIN.value == "invalid_chain"
    assert CertStatus.SELFSIGNED.value == "self_signed"


def test_cert_status_unique_values() -> None:
    values = [member.value for member in CertStatus]
    assert len(values) == len(set(values))


def test_cert_status_normalize_accepts_known_values() -> None:
    assert CertStatus.normalize("EXPIRED") is CertStatus.EXPIRED
    assert CertStatus.normalize("invalid chain") is CertStatus.INVALIDCHAIN
    assert CertStatus.normalize("self_signed") is CertStatus.SELFSIGNED
    assert CertStatus.normalize("self-signed") is CertStatus.SELFSIGNED
    assert CertStatus.normalize("invalid-chain") is CertStatus.INVALIDCHAIN

    assert CertStatus.normalize("expiring") is CertStatus.EXPIRING
    assert CertStatus.normalize("ok") is CertStatus.OK


def test_cert_status_normalize_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="unknown cert status: revoked"):
        CertStatus.normalize("revoked")


def test_cert_status_normalize_rejects_blank() -> None:
    with pytest.raises(ValueError, match="unknown cert status:"):
        CertStatus.normalize("   ")


def test_cert_status_min_severity_expired_at_least_high() -> None:
    assert CertStatus.EXPIRED.min_severity().rank >= Severity.HIGH.rank
    assert CertStatus.INVALIDCHAIN.min_severity().rank >= Severity.HIGH.rank


def test_cert_status_min_severity_below_critical() -> None:
    assert CertStatus.OK.min_severity() is Severity.LOW
    assert CertStatus.SELFSIGNED.min_severity() is Severity.MEDIUM
    assert CertStatus.EXPIRING.min_severity() is Severity.MEDIUM
