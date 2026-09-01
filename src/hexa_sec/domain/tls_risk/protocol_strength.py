"""ProtocolStrength — the strength of a TLS protocol (context: tls_risk, SEC-16).

Maps a negotiated protocol (SSLv3 → TLS 1.3) to a strength rank. Obsolete and
downgradable protocols impose a HIGH severity; normalization never guesses an
unknown protocol.
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.finding.severity import Severity

_RANK_BY_TOKEN: dict[str, tuple[str, int]] = {
    "sslv3": ("SSLv3", 0),
    "tls10": ("TLS 1.0", 1),
    "tlsv10": ("TLS 1.0", 1),
    "tls1": ("TLS 1.0", 1),
    "tlsv1": ("TLS 1.0", 1),
    "tls11": ("TLS 1.1", 2),
    "tlsv11": ("TLS 1.1", 2),
    "tls12": ("TLS 1.2", 3),
    "tlsv12": ("TLS 1.2", 3),
    "tls13": ("TLS 1.3", 4),
    "tlsv13": ("TLS 1.3", 4),
}


def _token(version: str) -> str:
    return version.strip().lower().replace(" ", "").replace(".", "").replace("-", "")


@dataclass(frozen=True)
class ProtocolStrength:
    """A negotiated TLS protocol with its strength rank."""

    version: str
    rank: int

    @property
    def is_obsolete(self) -> bool:
        """Whether the protocol is obsolete / vulnerable to downgrade."""
        return self.rank <= 2

    @property
    def min_severity(self) -> Severity:
        """The minimum severity imposed by this protocol strength."""
        if self.rank == 0:
            return Severity.CRITICAL
        if self.rank <= 2:
            return Severity.HIGH
        if self.rank == 3:
            return Severity.MEDIUM
        return Severity.LOW

    @classmethod
    def of(cls, version: str) -> ProtocolStrength:
        """Parse a protocol label; unknown protocols are rejected."""
        key = _token(version)
        if key not in _RANK_BY_TOKEN:
            raise ValueError(f"unknown protocol: {version}")
        label, rank = _RANK_BY_TOKEN[key]
        return cls(version=label, rank=rank)
