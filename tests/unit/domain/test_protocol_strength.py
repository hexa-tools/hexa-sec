"""Tests for the ProtocolStrength value object (context: tls_risk, SEC-16)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.tls_risk.protocol_strength import ProtocolStrength


def test_protocol_strength_of_known_versions() -> None:
    assert ProtocolStrength.of("SSLv3").rank == 0
    assert ProtocolStrength.of("TLS 1.0").rank == 1
    assert ProtocolStrength.of("TLSv1.1").rank == 2
    assert ProtocolStrength.of("TLS 1.2").rank == 3
    assert ProtocolStrength.of("TLSv1.3").rank == 4


def test_protocol_strength_rejects_unknown() -> None:
    with pytest.raises(ValueError):
        ProtocolStrength.of("TLS 9.9")


def test_protocol_strength_rejects_blank() -> None:
    with pytest.raises(ValueError):
        ProtocolStrength.of("   ")


def test_protocol_strength_is_obsolete() -> None:
    assert ProtocolStrength.of("SSLv3").is_obsolete is True
    assert ProtocolStrength.of("TLS 1.0").is_obsolete is True
    assert ProtocolStrength.of("TLS 1.2").is_obsolete is False
    assert ProtocolStrength.of("TLS 1.3").is_obsolete is False


def test_protocol_strength_min_severity_weak() -> None:
    assert ProtocolStrength.of("SSLv3").min_severity is Severity.CRITICAL
    assert ProtocolStrength.of("TLS 1.0").min_severity is Severity.HIGH
    assert ProtocolStrength.of("TLS 1.1").min_severity is Severity.HIGH


def test_protocol_strength_min_severity_strong() -> None:
    assert ProtocolStrength.of("TLS 1.2").min_severity is Severity.MEDIUM
    assert ProtocolStrength.of("TLS 1.3").min_severity is Severity.LOW
