"""GenerateReportServicePort — the client deliverable (US-5)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict


class ReportAction(TypedDict):
    """A « fix first » action: the failing finding, why, the fix and the effort."""

    finding_id: str
    issue: str
    why: str
    fix: str
    effort: str
    severity: str
    score: int


class ReportCorrelation(TypedDict):
    """A plain-language correlation, with its source findings (the proof)."""

    type: str
    reason: str
    findings: list[str]


class ReportFinding(TypedDict):
    """A technical detail finding, citing its scanner and its raw evidence."""

    finding_id: str
    title: str
    severity: str
    scanner: str
    evidence: str


class ReportCompliance(TypedDict):
    """A compliance score per framework (ISO/RGPD/NIS2/PCI-DSS)."""

    scope: str
    value: float


class GenerateReportCommand(TypedDict):
    """Input: the deterministic report data, carried by the command."""

    scan_id: str
    tenant_id: str
    title: str
    score: int
    previous_score: int | None
    ai_summary: str
    actions: tuple[ReportAction, ...]
    correlations: tuple[ReportCorrelation, ...]
    findings: tuple[ReportFinding, ...]
    compliance: tuple[ReportCompliance, ...]


class GenerateReportResult(TypedDict):
    """Output: the markdown report (the deliverable)."""

    report_id: str
    markdown: str


class GenerateReportServicePort(ABC):
    """Produce the 5-section report, with the SLM only writing the opening."""

    @abstractmethod
    def generate(self, command: GenerateReportCommand) -> GenerateReportResult:
        """Return the report for the scan."""
        raise NotImplementedError  # pragma: no cover
