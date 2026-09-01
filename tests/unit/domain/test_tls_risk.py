"""Tests for the TlsRisk inventory aggregate (context: tls_risk, SEC-16)."""

from __future__ import annotations

from hexa_sec.domain.tls_risk.cert_status import CertStatus
from hexa_sec.domain.tls_risk.protocol_strength import ProtocolStrength
from hexa_sec.domain.tls_risk.tls_finding import TlsFinding
from hexa_sec.domain.tls_risk.tls_risk import TlsRisk


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


def test_for_host_consolidates_findings() -> None:
    findings = (
        _finding(cert_status=CertStatus.EXPIRED),
        _finding(cert_status=CertStatus.OK, protocol="TLS 1.0"),
        _finding(cert_status=CertStatus.SELFSIGNED),
    )
    risk = TlsRisk.for_host("app.example", findings)
    assert risk.host == "app.example"
    assert len(risk.findings) == 3
    assert risk.risk_count == 3
    assert risk.critical_count == 1


def test_for_host_deduplicates_identical_findings() -> None:
    findings = (_finding(), _finding())
    risk = TlsRisk.for_host("app.example", findings)
    assert len(risk.findings) == 1


def test_for_host_keeps_distinct_protocols_separate() -> None:
    findings = (
        _finding(protocol="TLS 1.0", evidence="a"),
        _finding(protocol="TLS 1.2", evidence="b"),
    )
    risk = TlsRisk.for_host("app.example", findings)
    assert len(risk.findings) == 2


def test_for_host_keeps_self_signed() -> None:
    self_signed = _finding(cert_status=CertStatus.SELFSIGNED)
    risk = TlsRisk.for_host("app.example", (self_signed,))
    assert len(risk.findings) == 1


def test_for_host_ignores_other_host() -> None:
    risk = TlsRisk.for_host("app.example", (_finding(host="other.example"),))
    assert risk.findings == ()
    assert risk.risk_count == 0


def test_for_host_matches_normalized_host() -> None:
    padded = _finding(host="  app.example  ")
    risk = TlsRisk.for_host("app.example", (padded,))
    assert len(risk.findings) == 1


def test_for_host_no_findings_returns_empty() -> None:
    risk = TlsRisk.for_host("app.example", ())
    assert risk.findings == ()
    assert risk.risk_count == 0
    assert risk.critical_count == 0


def test_for_host_critical_count_only_critical() -> None:
    findings = (
        _finding(cert_status=CertStatus.EXPIRED),
        _finding(cert_status=CertStatus.OK, protocol="TLS 1.0"),
        _finding(cert_status=CertStatus.OK, protocol="TLS 1.3"),
    )
    risk = TlsRisk.for_host("app.example", findings)
    assert risk.critical_count == 1
    assert risk.risk_count == 3


def test_for_host_is_deterministic() -> None:
    findings = (
        _finding(cert_status=CertStatus.EXPIRED),
        _finding(cert_status=CertStatus.OK, protocol="TLS 1.0"),
    )
    first = TlsRisk.for_host("app.example", findings)
    second = TlsRisk.for_host("app.example", findings)
    assert first == second
    assert first.critical_count == second.critical_count


# --- Category: stabilité / déterminisme (tie-break sur evidence) ------------


def test_for_host_dedup_same_key_keeps_smallest_evidence() -> None:
    a = _finding(cert_status=CertStatus.OK, protocol="TLS 1.0", evidence="zzz")
    b = _finding(cert_status=CertStatus.OK, protocol="TLS 1.0", evidence="aaa")
    risk = TlsRisk.for_host("app.example", (a, b))
    assert len(risk.findings) == 1
    assert risk.findings[0].evidence == "aaa"


def test_for_host_dedup_order_independent_for_evidence() -> None:
    a = _finding(cert_status=CertStatus.OK, protocol="TLS 1.0", evidence="zzz")
    b = _finding(cert_status=CertStatus.OK, protocol="TLS 1.0", evidence="aaa")
    first = TlsRisk.for_host("app.example", (a, b))
    second = TlsRisk.for_host("app.example", (b, a))
    assert first == second
    assert first.findings[0].evidence == "aaa"
