"""ConfigScannerPort — the config/benchmark scanner boundary (driven port)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict


class ConfigFindingRecord(TypedDict):
    """A normalized configuration deviation."""

    benchmark: str
    check: str


class ConfigScannerPort(ABC):
    """Run a configuration scanner against a host."""

    @abstractmethod
    def scan(self, host: str) -> list[ConfigFindingRecord]:
        """Return normalized findings for ``host``."""
        raise NotImplementedError  # pragma: no cover
