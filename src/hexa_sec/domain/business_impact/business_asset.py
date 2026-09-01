"""BusinessAsset — an asset mapped to its business process (context: business_impact, SEC-23).

An asset always supports a named business process (invoice, payments...) and
carries an :class:`ImpactLevel`. Name and process are normalized so the asset is
never mis-matched in aggregation; a business asset without a process is rejected.
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.business_impact.impact_level import ImpactLevel


@dataclass(frozen=True)
class BusinessAsset:
    """An asset and the process it supports, with its business criticality."""

    name: str
    process: str
    impact_level: ImpactLevel

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("business asset name cannot be empty")
        if not self.process or not self.process.strip():
            raise ValueError("business asset process cannot be empty")
        if not isinstance(self.impact_level, ImpactLevel):
            raise ValueError("business asset impact_level must be an ImpactLevel")
        object.__setattr__(self, "name", self.name.strip())
        object.__setattr__(self, "process", self.process.strip())
