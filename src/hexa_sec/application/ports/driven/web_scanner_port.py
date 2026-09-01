"""WebScannerPort — the web scanner boundary (driven port)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict


class WebFindingRecord(TypedDict):
    """A normalized web finding produced by a web scanner."""

    title: str
    severity: str
    url: str


class WebScannerPort(ABC):
    """Run a web scanner against an asset and return normalized findings."""

    @abstractmethod
    def scan(self, asset: str) -> list[WebFindingRecord]:
        """Return normalized findings for ``asset``.

        Raises:
            ScannerUnavailableError: when the scanner cannot be reached.
            ScannerAuthError: when credentials are missing or invalid.
        """
        raise NotImplementedError  # pragma: no cover
