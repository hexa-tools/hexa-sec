"""TlsFinding — a TLS/certificate finding (context: tls_risk, SEC-16).

An adapter (sslscan/testssl/openscap) translates a scanner hit into a
TlsFinding: the host, its CertStatus, the negotiated ProtocolStrength and the
evidence. The severity is derived from both: an expired cert and an obsolete
protocol each impose a floor, so the finding is never under-stated.
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.tls_risk.cert_status import CertStatus
from hexa_sec.domain.tls_risk.protocol_strength import ProtocolStrength


@dataclass(frozen=True)
class TlsFinding:
    """A single certificate or protocol problem on a host."""

    host: str
    cert_status: CertStatus
    protocol: ProtocolStrength
    evidence: str

    @property
    def severity(self) -> Severity:
        """Derived severity: the higher of the status and protocol floors."""
        status_floor = self.cert_status.min_severity()
        protocol_floor = self.protocol.min_severity
        if status_floor.rank >= protocol_floor.rank:
            return status_floor
        return protocol_floor

    def __post_init__(self) -> None:
        if not self.host or not self.host.strip():
            raise ValueError("tls finding host cannot be empty")
        if not isinstance(self.cert_status, CertStatus):
            raise ValueError("tls finding cert_status must be a CertStatus")
        if not isinstance(self.protocol, ProtocolStrength):
            raise ValueError("tls finding protocol must be a ProtocolStrength")
        if not self.evidence or not self.evidence.strip():
            raise ValueError("tls finding requires evidence (proof)")
        object.__setattr__(self, "host", self.host.strip())
