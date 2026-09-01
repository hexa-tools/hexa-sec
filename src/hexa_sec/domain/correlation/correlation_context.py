"""CorrelationContext — the deterministic inputs around the correlation checker."""

from __future__ import annotations

from dataclasses import dataclass, field

from hexa_sec.domain.asset.asset import AssetId
from hexa_sec.domain.asset.asset_criticality import AssetCriticality
from hexa_sec.domain.correlation.correlation_input import CorrelationInput


@dataclass(frozen=True)
class CorrelationContext:
    """Thresholds and surrounding data the checker needs (all deterministic)."""

    exposure_open_ports: int = 3
    noise_count: int = 10
    asset_criticalities: dict[AssetId, AssetCriticality] = field(default_factory=dict)
    previous: tuple[CorrelationInput, ...] = ()

    def __post_init__(self) -> None:
        if self.exposure_open_ports < 1:
            raise ValueError("exposure threshold must be at least 1")
        if self.noise_count < 1:
            raise ValueError("noise threshold must be at least 1")

    def criticality_of(self, asset: AssetId) -> AssetCriticality | None:
        return self.asset_criticalities.get(asset)
