"""Threat — a known threat actor/campaign (context: threat_intel, SEC-20).

A known threat (actor, tactic, severity) that can be linked, with proof, to
assets and findings via the related CVE findings. A threat never claims an asset
without a finding as proof — no speculation.
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.asset.asset import AssetId
from hexa_sec.domain.finding.finding import FindingId
from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.threat_intel.ioc import Ioc
from hexa_sec.domain.threat_intel.threat_actor import ThreatActor


@dataclass(frozen=True)
class Threat:
    """A known threat with optional, proven links to assets/findings/IOCs."""

    actor: ThreatActor
    tactic: str
    severity: Severity
    related_assets: tuple[AssetId, ...] = ()
    related_findings: tuple[FindingId, ...] = ()
    iocs: tuple[Ioc, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.actor, ThreatActor):
            raise ValueError("threat actor must be a ThreatActor")
        if not self.tactic or not self.tactic.strip():
            raise ValueError("threat tactic cannot be empty")
        if not isinstance(self.severity, Severity):
            raise ValueError("threat severity must be a Severity")
        if self.related_assets and not self.related_findings:
            raise ValueError("threat claiming assets requires finding proof")
        object.__setattr__(self, "tactic", self.tactic.strip())
