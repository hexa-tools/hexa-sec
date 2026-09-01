"""CertStatus — the certificate status (context: tls_risk, SEC-16).

The status of a TLS certificate drives a minimum severity: an expired cert must
never be LOW, an invalid chain is critical, a self-signed cert on an internal
host is tolerated but flagged. Normalization never invents a status.
"""

from __future__ import annotations

from enum import Enum

from hexa_sec.domain.finding.severity import Severity


class CertStatus(Enum):
    """The state of a TLS certificate."""

    OK = "ok"
    EXPIRED = "expired"
    EXPIRING = "expiring"
    INVALIDCHAIN = "invalid_chain"
    SELFSIGNED = "self_signed"

    def min_severity(self) -> Severity:
        """The minimum severity imposed by this certificate status."""
        if self is CertStatus.EXPIRED or self is CertStatus.INVALIDCHAIN:
            return Severity.CRITICAL
        if self is CertStatus.SELFSIGNED or self is CertStatus.EXPIRING:
            return Severity.MEDIUM
        return Severity.LOW

    @classmethod
    def normalize(cls, raw: str) -> CertStatus:
        """Map a raw label to a ``CertStatus``; unknown values are rejected."""
        cleaned = raw.strip().lower().replace(" ", "_").replace("-", "_")
        try:
            return cls(cleaned)
        except ValueError as error:
            raise ValueError(f"unknown cert status: {raw}") from error
