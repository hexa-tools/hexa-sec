"""ScanAssetServicePort — launching a scan on an asset (US-1)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict

from hexa_sec.application.ports.driven.code_scanner_port import CodeFindingRecord
from hexa_sec.application.ports.driven.network_scanner_port import NetworkFindingRecord
from hexa_sec.application.ports.driven.web_scanner_port import WebFindingRecord

FindingRecord = WebFindingRecord | NetworkFindingRecord | CodeFindingRecord


class ScanAssetCommand(TypedDict):
    """Input: a mandate-authorized scan request."""

    asset: str
    mandate_id: str
    vendor: str
    tenant_id: str
    depth: str
    exclusions: tuple[str, ...]


class ScanAssetResult(TypedDict):
    """Output: the created scan, its trace and the normalized findings."""

    scan_id: str
    status: str
    mandate_id: str
    findings: list[FindingRecord]


class ScanAssetServicePort(ABC):
    """Launch scanners on an asset, **after** the mandate check (law Godfrain)."""

    @abstractmethod
    def scan(self, command: ScanAssetCommand) -> ScanAssetResult:
        """Run the scan. Refuses without a covering, valid mandate.

        Raises:
            MandateNotFoundError: no mandate exists.
            MandateScopeError: target outside the mandate scope.
            MandateExpiredError: mandate is expired.
            MandateLevelError: insufficient level for an offensive depth.
            ScannerUnavailableError / ScannerAuthError / ScannerTimeoutError:
                a scanner failed (normalized by the adapter).
        """
        raise NotImplementedError  # pragma: no cover
