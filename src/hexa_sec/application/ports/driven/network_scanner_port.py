"""NetworkScannerPort — the network/infra scanner boundary (driven port)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict


class NetworkFindingRecord(TypedDict):
    """A normalized network finding."""

    host: str
    port: int
    service: str


class NetworkScannerPort(ABC):
    """Run a network scanner against an asset."""

    @abstractmethod
    def scan(self, asset: str) -> list[NetworkFindingRecord]:
        """Return normalized findings for ``asset``."""
        raise NotImplementedError  # pragma: no cover
