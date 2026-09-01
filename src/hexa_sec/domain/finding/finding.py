"""FindingId + Finding — a normalized scanner observation (context: finding).

A :class:`Finding` is the uniform shape every scanner adapter produces. It
never knows which scanner produced it — that trace lives in the evidence.
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.finding.confidence import Confidence
from hexa_sec.domain.finding.severity import Severity


@dataclass(frozen=True)
class FindingId:
    """An absolute identifier for a finding."""

    value: str


@dataclass(frozen=True)
class Finding:
    """A normalized finding, independent of its source scanner."""

    finding_id: FindingId | None
    title: str
    severity: Severity = Severity.MEDIUM
    confidence: Confidence = Confidence.MEDIUM

    def __post_init__(self) -> None:
        if not self.title:
            raise ValueError("finding title cannot be empty")

    def is_critical(self) -> bool:
        return self.severity is Severity.CRITICAL
