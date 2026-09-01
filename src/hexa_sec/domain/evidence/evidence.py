"""EvidenceId + Evidence — the proof behind each finding (context: evidence).

Every finding must cite its source scanner and its raw evidence. No report is
produced without evidence.
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.finding.finding import FindingId


@dataclass(frozen=True)
class EvidenceId:
    """An absolute identifier for a piece of evidence."""

    value: str


@dataclass(frozen=True)
class Evidence:
    """The raw, traceable proof of a finding."""

    evidence_id: EvidenceId
    finding_id: FindingId | None
    scanner: str
    detail: str

    def __post_init__(self) -> None:
        if not self.scanner:
            raise ValueError("evidence requires a source scanner")
        if not self.detail:
            raise ValueError("evidence detail cannot be empty")


@dataclass(frozen=True)
class EvidenceSet:
    """A collection of evidence attached to one finding."""

    evidence: tuple[Evidence, ...]
