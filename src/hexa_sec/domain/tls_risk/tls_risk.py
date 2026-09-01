"""TlsRisk — the consolidated TLS/certificate inventory (context: tls_risk, SEC-16).

``for_host`` groups findings under a host and deduplicates by
(host, cert_status, protocol): two distinct protocols stay separate (never
merged), a self-signed cert is kept (tolerated, flagged). On a duplicate the
smallest evidence wins, since the severity is fully determined by the key —
deterministic, independent of arrival order.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.tls_risk.tls_finding import TlsFinding


@dataclass(frozen=True)
class TlsRisk:
    """The inventory of TLS findings for a single host."""

    host: str
    findings: tuple[TlsFinding, ...]

    @property
    def risk_count(self) -> int:
        """Number of TLS findings."""
        return len(self.findings)

    @property
    def critical_count(self) -> int:
        """Number of findings at CRITICAL severity."""
        return sum(1 for finding in self.findings if finding.severity is Severity.CRITICAL)

    @classmethod
    def for_host(cls, host: str, findings: Iterable[TlsFinding]) -> TlsRisk:
        """Build a consolidated inventory, deduplicated by (host, status, protocol)."""
        seen: dict[tuple[str, str, str], TlsFinding] = {}
        for finding in findings:
            if finding.host != host:
                continue
            key = (finding.host, finding.cert_status.value, finding.protocol.version)
            existing = seen.get(key)
            if existing is None or finding.evidence < existing.evidence:
                seen[key] = finding
        return cls(host=host, findings=tuple(seen.values()))
