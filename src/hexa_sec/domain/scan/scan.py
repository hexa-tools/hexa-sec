"""ScanId + Scan — the orchestration of scanners on assets (context: scan).

A scan is always bound to a mandate. Vendors are opaque names — the domain
never knows how a scanner works, only which vendors were run.
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.asset.asset import AssetId
from hexa_sec.domain.consent.mandate import MandateId
from hexa_sec.domain.scan.scan_status import ScanStatus


@dataclass(frozen=True)
class ScanId:
    """An absolute identifier for a scan."""

    value: str


@dataclass(frozen=True)
class Scan:
    """The orchestration unit linking a mandate, assets and vendors."""

    scan_id: ScanId
    mandate_id: MandateId | None
    assets: tuple[AssetId, ...]
    vendors: tuple[str, ...]
    status: ScanStatus = ScanStatus.PENDING

    def __post_init__(self) -> None:
        if self.mandate_id is None:
            raise ValueError("scan requires a valid mandate id")
        if not self.assets:
            raise ValueError("scan requires at least one asset")

    def with_status(self, status: ScanStatus) -> Scan:
        return Scan(
            scan_id=self.scan_id,
            mandate_id=self.mandate_id,
            assets=self.assets,
            vendors=self.vendors,
            status=status,
        )
