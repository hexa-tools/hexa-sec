"""ManageMandateServicePort — the legal consent gate (US-4)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict


class ManageMandateCommand(TypedDict):
    """Input: what the client authorizes."""

    client: str
    targets: list[str]
    start_date: str
    end_date: str
    level: str


class ManageMandateResult(TypedDict):
    """Output: the created mandate."""

    mandate_id: str
    level: str


class ManageMandateServicePort(ABC):
    """Create and record the legal mandate. No scan runs without it."""

    @abstractmethod
    def create(self, command: ManageMandateCommand) -> ManageMandateResult:
        """Register a signed mandate."""
        raise NotImplementedError  # pragma: no cover
