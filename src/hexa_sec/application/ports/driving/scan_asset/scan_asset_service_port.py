"""ScanAssetServicePort — launching a scan on an asset (US-1)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict


class ScanAssetCommand(TypedDict):
    """Input: a mandate-authorized scan request."""

    asset: str
    mandate_id: str
    vendor: str


class ScanAssetResult(TypedDict):
    """Output: the created scan."""

    scan_id: str
    status: str


class ScanAssetServicePort(ABC):
    """Launch scanners on an asset, **after** the mandate check (law Godfrain)."""

    @abstractmethod
    def scan(self, command: ScanAssetCommand) -> ScanAssetResult:
        """Run the scan. Refuses without a covering, valid mandate.

        Raises:
            MandateNotFoundError: no mandate exists.
            MandateScopeError: target outside the mandate scope.
            MandateExpiredError: mandate is expired.
        """
        raise NotImplementedError  # pragma: no cover
