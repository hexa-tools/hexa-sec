"""WifiRisk — the consolidated wireless inventory (context: wifi_risk).

``of`` deduplicates findings by (ssid, bssid) keeping the most severe posture and
sorts deterministically. Nothing raises when no network is weak.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from hexa_sec.domain.wifi_risk.wifi_finding import WifiFinding


@dataclass(frozen=True)
class WifiRisk:
    """The wireless findings of the audited networks."""

    findings: tuple[WifiFinding, ...]

    @property
    def weak_count(self) -> int:
        """Number of weak networks (open/WEP/WPA)."""
        return sum(1 for finding in self.findings if finding.weak)

    @property
    def rogue_count(self) -> int:
        """Number of rogue access points."""
        return sum(1 for finding in self.findings if finding.is_rogue())

    def weak_networks(self) -> tuple[str, ...]:
        """The SSIDs of weak networks, sorted."""
        return tuple(sorted(finding.ssid.value for finding in self.findings if finding.weak))

    @classmethod
    def of(cls, findings: Iterable[WifiFinding]) -> WifiRisk:
        """Build the inventory, deduplicated by (ssid, bssid) (most severe kept)."""
        seen: dict[tuple[str, str | None], WifiFinding] = {}
        for finding in findings:
            key = (finding.ssid.value, finding.bssid.value if finding.bssid else None)
            existing = seen.get(key)
            if existing is None or _prefer(finding, existing):
                seen[key] = finding
        return cls(
            tuple(
                sorted(
                    seen.values(),
                    key=lambda f: (f.ssid.value, f.bssid.value if f.bssid else ""),
                )
            )
        )


def _severity(finding: WifiFinding) -> tuple[int, int, int]:
    """(rogue, weak, clients) — higher is worse; total order for determinism."""
    return (int(finding.is_rogue()), int(finding.weak), finding.clients)


def _prefer(candidate: WifiFinding, current: WifiFinding) -> bool:
    """Whether ``candidate`` should replace ``current`` for the same key."""
    return _severity(candidate) > _severity(current)
