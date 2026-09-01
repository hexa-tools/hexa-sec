"""ThreatIntel — the consolidated threat inventory (context: threat_intel, SEC-20).

``for_asset`` returns the known threats that touch an asset, deduplicated by
(actor, tactic): the highest severity (then a deterministic canonical link) wins,
independent of arrival order. Abstract threats (no asset link) are excluded and
nothing raises when the asset is untouched.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from hexa_sec.domain.threat_intel.threat import Threat


@dataclass(frozen=True)
class ThreatIntel:
    """The inventory of known threats affecting a single asset."""

    asset: str
    threats: tuple[Threat, ...]

    @property
    def threat_count(self) -> int:
        """Number of known threats affecting the asset."""
        return len(self.threats)

    @classmethod
    def for_asset(cls, asset: str, threats: Iterable[Threat]) -> ThreatIntel:
        """Build the deduplicated threats touching ``asset``."""
        normalized = asset.strip()
        if not normalized:
            raise ValueError("threat asset cannot be empty")
        relevant = [
            t for t in threats if any(a.value.strip() == normalized for a in t.related_assets)
        ]
        deduped = _dedup(relevant)
        return cls(asset=normalized, threats=deduped)


def _sort_key(threat: Threat) -> tuple[int, tuple[str, ...], tuple[str, ...]]:
    """Severity first, then a deterministic canonical link (assets, findings)."""
    assets = tuple(sorted(a.value for a in threat.related_assets))
    findings = tuple(sorted(f.value for f in threat.related_findings))
    return (threat.severity.rank, assets, findings)


def _prefer(candidate: Threat, current: Threat) -> bool:
    """Whether ``candidate`` should replace ``current`` (order-independent fold)."""
    return _sort_key(candidate) > _sort_key(current)


def _dedup(threats: Iterable[Threat]) -> tuple[Threat, ...]:
    """Keep the highest-severity threat per (actor, tactic), deterministically."""
    best: dict[tuple[str, str], Threat] = {}
    for threat in threats:
        key = (threat.actor.identifier, threat.tactic)
        existing = best.get(key)
        if existing is None or _prefer(threat, existing):
            best[key] = threat
    return tuple(sorted(best.values(), key=lambda t: (t.actor.identifier, t.tactic)))
