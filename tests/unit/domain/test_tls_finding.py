"""Tests for TlsFinding (context: tls_risk, SEC-16)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.tls_risk.cert_status import CertStatus
from hexa_sec.domain.tls_risk.protocol_strength import ProtocolStrength
from hexa_sec.domain.tls_risk.tls_finding import TlsFinding


def _finding(
    host: str = "app.example",
    cert_status: CertStatus = CertStatus.OK,
    protocol: str = "TLS 1.3",
    evidence: str = "cert: sha256:abc",
) -> TlsFinding:
    return TlsFinding(
        host=host,
        cert_status=cert_status,
        protocol=ProtocolStrength.of(protocol),
        evidence=evidence,
    )


def test_tls_finding_creation() -> None:
    finding = _finding()
    assert finding.host == "app.example"
    assert finding.cert_status is CertStatus.OK
    assert finding.protocol.version == "TLS 1.3"
    assert finding.evidence == "cert: sha256:abc"


def test_tls_finding_rejects_empty_host() -> None:
    with pytest.raises(ValueError):
        _finding(host="")


def test_tls_finding_rejects_blank_host() -> None:
    with pytest.raises(ValueError):
        _finding(host="   ")


def test_tls_finding_normalizes_host() -> None:
    assert _finding(host="  app.example  ").host == "app.example"


def test_tls_finding_rejects_non_cert_status() -> None:
    with pytest.raises(ValueError):
        TlsFinding(
            host="app.example",
            cert_status="expired",
            protocol=ProtocolStrength.of("TLS 1.3"),
            evidence="cert: sha256:abc",
        )


def test_tls_finding_rejects_non_protocol() -> None:
    with pytest.raises(ValueError):
        TlsFinding(
            host="app.example",
            cert_status=CertStatus.OK,
            protocol="TLS 1.3",
            evidence="cert: sha256:abc",
        )


def test_tls_finding_rejects_empty_evidence() -> None:
    with pytest.raises(ValueError):
        _finding(evidence="")


def test_tls_finding_rejects_blank_evidence() -> None:
    with pytest.raises(ValueError):
        _finding(evidence="   ")


def test_tls_finding_severity_expired_at_least_high() -> None:
    assert _finding(cert_status=CertStatus.EXPIRED).severity.rank >= Severity.HIGH.rank


def test_tls_finding_severity_weak_protocol_is_high() -> None:
    assert _finding(protocol="TLS 1.0").severity is Severity.HIGH


def test_tls_finding_severity_valid_is_low() -> None:
    assert _finding(protocol="TLS 1.3").severity is Severity.LOW


def test_tls_finding_severity_self_signed_internal_adapted() -> None:
    assert _finding(cert_status=CertStatus.SELFSIGNED).severity is Severity.MEDIUM
