"""BusinessImpact — the business-critical assets for a name (context: business_impact, SEC-23).

``for_asset`` returns the business assets mapped to a name, deduplicated by
(name, process) and sorted deterministically. Nothing raises when an asset has no
business mapping.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from hexa_sec.domain.business_impact.business_asset import BusinessAsset
from hexa_sec.domain.business_impact.impact_level import ImpactLevel


@dataclass(frozen=True)
class BusinessImpact:
    """The business-critical assets of a logical asset name."""

    name: str
    assets: tuple[BusinessAsset, ...]

    @property
    def critical_count(self) -> int:
        """Number of business-critical assets."""
        return sum(1 for asset in self.assets if asset.impact_level.is_critical)

    def critical_assets(self) -> tuple[BusinessAsset, ...]:
        """The business-critical assets, sorted by process."""
        return tuple(asset for asset in self.assets if asset.impact_level is ImpactLevel.CRITICAL)

    @classmethod
    def for_asset(cls, name: str, assets: Iterable[BusinessAsset]) -> BusinessImpact:
        """Build the deduplicated business assets for ``name``."""
        normalized = name.strip()
        if not normalized:
            raise ValueError("business asset name cannot be empty")
        relevant = [a for a in assets if a.name == normalized]
        deduped = _dedup(relevant)
        return cls(name=normalized, assets=deduped)


def _dedup(assets: Iterable[BusinessAsset]) -> tuple[BusinessAsset, ...]:
    """Keep the highest-impact asset per (name, process), then sort deterministically."""
    seen: dict[tuple[str, str], BusinessAsset] = {}
    for asset in assets:
        key = (asset.name, asset.process)
        existing = seen.get(key)
        if existing is None or asset.impact_level.rank > existing.impact_level.rank:
            seen[key] = asset
    return tuple(sorted(seen.values(), key=lambda a: (a.name, a.process)))
