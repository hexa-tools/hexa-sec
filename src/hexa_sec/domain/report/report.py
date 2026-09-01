"""ReportId + Report — the audit deliverable shell (context: report, SEC-8).

``Report`` is the structured deliverable: a title + five ordered sections
(score global, top-5 fix-first, correlations, technical detail, compliance).
Sections may be empty (a report with no findings renders empty sections, not a
failure). The top-5 never exceeds five actions.
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.compliance.compliance_score import ComplianceScore
from hexa_sec.domain.correlation.correlation import Correlation
from hexa_sec.domain.finding.finding import Finding
from hexa_sec.domain.report.priority_action import PriorityAction
from hexa_sec.domain.report.report_section import ReportSection
from hexa_sec.domain.scoring.risk_score import RiskScore


@dataclass(frozen=True)
class ReportId:
    """An absolute identifier for a report."""

    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("report id cannot be empty")


@dataclass(frozen=True)
class Report:
    """The structured audit deliverable."""

    report_id: ReportId
    title: str
    global_score: RiskScore | None = None
    top_actions: tuple[PriorityAction, ...] = ()
    correlations: tuple[Correlation, ...] = ()
    detail: tuple[Finding, ...] = ()
    compliance: tuple[ComplianceScore, ...] = ()

    def __post_init__(self) -> None:
        if not self.title or not self.title.strip():
            raise ValueError("report title cannot be empty")
        if len(self.top_actions) > 5:
            raise ValueError("report top actions cannot exceed 5")

    def sections(self) -> tuple[ReportSection, ...]:
        """The five sections in their canonical client-facing order."""
        return (
            ReportSection.SCORE,
            ReportSection.TOP_FIVE,
            ReportSection.CORRELATIONS,
            ReportSection.DETAIL,
            ReportSection.COMPLIANCE,
        )
