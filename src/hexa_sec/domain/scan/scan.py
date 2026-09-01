"""ScanId + Scan — the orchestration unit (context: scan, SEC-4).

A scan is always bound to a **mandate**: it checks that the mandate exists, is
valid, covers every target, and is of sufficient level for an offensive depth.
Excluded hosts are never scanned. Status transitions are strictly validated.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

from hexa_sec.domain.asset.asset import Asset
from hexa_sec.domain.consent.mandate import Mandate, MandateId
from hexa_sec.domain.errors import (
    MandateExpiredError,
    MandateLevelError,
    MandateNotFoundError,
    MandateScopeError,
)
from hexa_sec.domain.scan.scan_parameters import ScanParameters
from hexa_sec.domain.scan.scan_status import ScanStatus


@dataclass(frozen=True)
class ScanId:
    """An absolute identifier for a scan."""

    value: str


@dataclass(frozen=True)
class Scan:
    """The orchestration unit linking a mandate, assets, vendors and parameters."""

    scan_id: ScanId
    mandate: Mandate
    assets: tuple[Asset, ...]
    vendors: tuple[str, ...]
    parameters: ScanParameters
    status: ScanStatus = ScanStatus.PENDING

    def __post_init__(self) -> None:
        if not self.assets:
            raise ValueError("scan requires at least one asset")
        scanned = {asset.name for asset in self.assets}
        violated = [exclusion for exclusion in self.parameters.exclusions if exclusion in scanned]
        if violated:
            raise ValueError(f"scan must never scan excluded hosts: {violated}")

    @property
    def mandate_id(self) -> MandateId:
        return self.mandate.mandate_id

    @classmethod
    def create(
        cls,
        scan_id: ScanId,
        mandate: Mandate | None,
        assets: Iterable[Asset],
        vendors: Iterable[str],
        parameters: ScanParameters,
        as_of: date | None = None,
    ) -> Scan:
        """Build a Scan, protecting the mandate and scope invariants (Godfrain)."""
        if mandate is None:
            raise MandateNotFoundError("no mandate for the requested scan")
        cls._validate_mandate(mandate, assets, parameters, as_of)
        return cls(scan_id, mandate, tuple(assets), tuple(vendors), parameters)

    @staticmethod
    def _validate_mandate(
        mandate: Mandate,
        assets: Iterable[Asset],
        parameters: ScanParameters,
        as_of: date | None,
    ) -> None:
        if not mandate.is_valid(as_of):
            raise MandateExpiredError(
                "mandate is expired for this scan", {"mandate_id": mandate.mandate_id.value}
            )
        for asset in assets:
            if not mandate.covers(asset.name):
                raise MandateScopeError(
                    f"asset {asset.name} is outside the mandate scope",
                    {"target": asset.name},
                )
        if parameters.depth.requires_offensive_mandate() and not mandate.is_offensive():
            raise MandateLevelError("offensive depth requires an offensive mandate")

    def with_status(self, status: ScanStatus) -> Scan:
        if not self.status.can_transition_to(status):
            raise ValueError(f"illegal scan transition: {self.status.value} -> {status.value}")
        return Scan(
            scan_id=self.scan_id,
            mandate=self.mandate,
            assets=self.assets,
            vendors=self.vendors,
            parameters=self.parameters,
            status=status,
        )
