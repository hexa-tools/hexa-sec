"""NetworkRisk — the consolidated exposure inventory (context: network_risk).

``for_asset`` turns raw findings into a deduplicated inventory for one asset,
dropping any finding without banner evidence (no speculation). It never raises
when nothing is found — an empty inventory is the normal answer.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from hexa_sec.domain.network_risk.network_finding import NetworkFinding


@dataclass(frozen=True)
class NetworkRisk:
    """The inventory of network findings for a single asset."""

    asset: str
    findings: tuple[NetworkFinding, ...]

    @property
    def exposed_count(self) -> int:
        """Number of findings classified as Internet-exposed."""
        return sum(1 for finding in self.findings if finding.exposure.is_exposed())

    @property
    def exposed_ports(self) -> tuple[int, ...]:
        """Port numbers exposed to the Internet, sorted ascending."""
        return tuple(
            sorted(
                {finding.port.number for finding in self.findings if finding.exposure.is_exposed()}
            )
        )

    @classmethod
    def for_asset(cls, asset: str, findings: Iterable[NetworkFinding]) -> NetworkRisk:
        """Build a consolidated inventory, deduplicated and evidence-checked.

        Findings are canonicalized by (asset, port, service): a duplicate keeps
        the first occurrence. A finding whose banner is absent (no evidence) is
        dropped as speculation.
        """
        seen: set[tuple[str, int, str]] = set()
        consolidated: list[NetworkFinding] = []
        for finding in findings:
            if finding.asset != asset:
                continue
            if not finding.banner.is_present:
                continue
            key = (finding.asset, finding.port.number, finding.service.name)
            if key in seen:
                continue
            seen.add(key)
            consolidated.append(finding)
        return cls(asset=asset, findings=tuple(consolidated))
