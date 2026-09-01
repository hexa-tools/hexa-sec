"""ReportStorePort — the report persistence boundary (driven port)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict


class ReportRecord(TypedDict):
    """A persisted report."""

    report_id: str
    tenant_id: str
    title: str
    content: str


class ReportStorePort(ABC):
    """Persist and load reports."""

    @abstractmethod
    def save(self, record: ReportRecord) -> None:
        """Persist ``record``."""
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def load(self, report_id: str) -> ReportRecord | None:
        """Return the report ``report_id`` or ``None``."""
        raise NotImplementedError  # pragma: no cover
