"""KnowledgePort — the external knowledge boundary (driven port)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict


class CveRecord(TypedDict):
    """A known CVE with its scoring."""

    cve: str
    cvss: float
    epss: float


class KnowledgePort(ABC):
    """Enrich findings from external knowledge sources (NVD, EPSS, ...)."""

    @abstractmethod
    def epss(self, cve: str) -> float | None:
        """Return the EPSS probability for ``cve``, or ``None`` if unknown."""
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def cves(self, product: str) -> list[CveRecord]:
        """Return known CVEs for ``product``."""
        raise NotImplementedError  # pragma: no cover
