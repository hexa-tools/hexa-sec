"""CorrelateServicePort — the product's core (US-2)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict

from hexa_sec.domain.asset.asset import AssetId
from hexa_sec.domain.asset.asset_criticality import AssetCriticality
from hexa_sec.domain.correlation.correlation_input import CorrelationInput


class CorrelationRecord(TypedDict):
    """A correlation serialized for the report: type, reason and evidence."""

    type: str
    reason: str
    findings: list[str]
    impact: str


class CorrelateCommand(TypedDict):
    """Input: the normalized signals and the deterministic context to cross."""

    scan_id: str
    signals: tuple[CorrelationInput, ...]
    previous: tuple[CorrelationInput, ...]
    asset_criticalities: dict[AssetId, AssetCriticality]
    exposure_open_ports: int
    noise_count: int


class CorrelateResult(TypedDict):
    """Output: the correlations found, each with its source findings (evidence)."""

    scan_id: str
    correlations: list[CorrelationRecord]


class CorrelateServicePort(ABC):
    """Deterministic crossing of findings into insights. Never speculative."""

    @abstractmethod
    def correlate(self, command: CorrelateCommand) -> CorrelateResult:
        """Return the deterministic correlations for the normalized signals."""
        raise NotImplementedError  # pragma: no cover
