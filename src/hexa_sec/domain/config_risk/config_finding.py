"""ConfigFinding — a configuration deviation (context: config_risk, SEC-15).

An adapter (openscap/lynis/ciscat) translates a scanner hit into a ConfigFinding:
the asset, its BenchmarkId, the ConfigCheck, the Severity and the evidence.
Without evidence (check/preuve) there is no finding — no invented deviation.
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.config_risk.benchmark_id import BenchmarkId
from hexa_sec.domain.config_risk.config_check import ConfigCheck
from hexa_sec.domain.finding.severity import Severity


@dataclass(frozen=True)
class ConfigFinding:
    """A single benchmark deviation on an asset."""

    asset: str
    benchmark_id: BenchmarkId
    check: ConfigCheck
    severity: Severity
    evidence: str

    def __post_init__(self) -> None:
        if not self.asset or not self.asset.strip():
            raise ValueError("config finding asset cannot be empty")
        if not isinstance(self.benchmark_id, BenchmarkId):
            raise ValueError("config finding benchmark_id must be a BenchmarkId")
        if not isinstance(self.check, ConfigCheck):
            raise ValueError("config finding check must be a ConfigCheck")
        if not isinstance(self.severity, Severity):
            raise ValueError("config finding severity must be a Severity")
        if not self.evidence or not self.evidence.strip():
            raise ValueError("config finding requires evidence (proof)")
