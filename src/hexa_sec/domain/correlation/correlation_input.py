"""CorrelationInput — a normalized finding signal fed to the checker.

The checker works on these; adapters (Phase 3) translate scanner findings into
:class:`CorrelationInput` so the domain never touches a scanner format.
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.asset.asset import AssetId
from hexa_sec.domain.correlation.finding_kind import FindingKind
from hexa_sec.domain.finding.finding import FindingId
from hexa_sec.domain.finding.severity import Severity


@dataclass(frozen=True)
class CorrelationInput:
    """A single, normalized finding available for correlation."""

    finding_id: FindingId
    kind: FindingKind
    severity: Severity
    assets: tuple[AssetId, ...] = ()
    detail: str = ""
