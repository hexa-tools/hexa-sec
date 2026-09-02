"""ScoreReportService — deterministic fix-first ordering (US-3).

A pure orchestrator over the deterministic scoring domain: it builds a
:class:`ScoreComponents` per item, computes the ``RiskScore``, sorts by score
(fix-first), and derives the global posture (max). Never a guess, never random,
no try/catch (R6).
"""

from __future__ import annotations

from hexa_sec.application.ports.driving.score_report.score_report_service_port import (
    ScoredItem,
    ScoreItem,
    ScoreReportCommand,
    ScoreReportResult,
    ScoreReportServicePort,
)
from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.scoring.risk_score import RiskScore
from hexa_sec.domain.scoring.score_components import ScoreComponents
from hexa_sec.domain.scoring.score_level import ScoreLevel
from hexa_sec.domain.scoring.scoring_engine import compute_score


class ScoreReportService(ScoreReportServicePort):
    """Score and order, deterministically."""

    def score(self, command: ScoreReportCommand) -> ScoreReportResult:
        ordered = [self._score_item(item) for item in command["items"]]
        ordered.sort(key=lambda scored: (-scored["score"], scored["finding_id"]))
        top = ordered[0] if ordered else None
        return ScoreReportResult(
            scan_id=command["scan_id"],
            score=top["score"] if top else 0,
            label=top["label"] if top else ScoreLevel.LOW.value,
            ordered=tuple(ordered),
        )

    @staticmethod
    def _score_item(item: ScoreItem) -> ScoredItem:
        components = ScoreComponents(
            severity=Severity(item["severity"]),
            exploitability=item["exploitability"],
            exposure=item["exposure"],
            impact=item["impact"],
            facility=item["facility"],
        )
        # ScoreItem severity is required, so compute_score never returns None —
        # the ``or`` fallback is a defensive type-guard, never a real absence.
        risk_score = compute_score(components) or RiskScore.from_value(0.0)
        return ScoredItem(
            finding_id=item["finding_id"],
            score=int(round(risk_score.value)),
            label=risk_score.label,
        )
