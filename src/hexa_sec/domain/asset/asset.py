"""AssetId + Asset — the unit of what is audited (context: asset).

Pure domain: an asset has an identity, a type, and a business criticality.
No scanner knowledge lives here.
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.asset.asset_criticality import AssetCriticality
from hexa_sec.domain.asset.asset_type import AssetType


@dataclass(frozen=True)
class AssetId:
    """An absolute identifier for an asset."""

    value: str


@dataclass(frozen=True)
class Asset:
    """A single audited asset."""

    name: str
    type: AssetType
    asset_id: AssetId | None = None
    criticality: AssetCriticality = AssetCriticality.PUBLIC

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("asset name cannot be empty")

    def is_web(self) -> bool:
        return self.type is AssetType.WEB_APP

    def is_exposed(self) -> bool:
        return self.type is AssetType.WEB_APP or self.type is AssetType.HOST
