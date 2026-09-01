"""BusinessAsset — an asset tied to a business process (context: business_impact)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BusinessAsset:
    """An asset mapped to the process it supports."""

    name: str
    process: str

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("business asset name cannot be empty")
        if not self.process:
            raise ValueError("business asset process cannot be empty")
