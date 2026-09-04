"""GenerateReportService — the client deliverable (US-5).

Assembles the 5-section audit report **in the canonical order** (score global,
top-5 fix-first, correlations, technical detail, compliance) from the
deterministic data carried by the command. Pure and deterministic: no I/O, no
LLM decision — the SLM opening is only embedded when the command provides one
(empty summary → omitted, the report stays valid). Never try/catch (R6).

No report without proof: a correlation without source findings is rejected, and
a finding without scanner/evidence never reaches the technical detail.
"""

from __future__ import annotations

from hexa_sec.application.ports.driving.generate_report.generate_report_service_port import (
    GenerateReportCommand,
    GenerateReportResult,
    GenerateReportServicePort,
)
from hexa_sec.domain.compliance.compliance_scope import ComplianceScope
from hexa_sec.domain.scoring.risk_score import RiskScore

_FRAMEWORK_ORDER = (
    ComplianceScope.ISO_27001,
    ComplianceScope.RGPD,
    ComplianceScope.NIS2,
    ComplianceScope.PCI_DSS,
)


class GenerateReportService(GenerateReportServicePort):
    """Produce the 5-section markdown deliverable, deterministically."""

    def generate(self, command: GenerateReportCommand) -> GenerateReportResult:
        # Deterministic: the same scan always yields the same report id, so a
        # report regenerated twice is deduplicated by ReportId (idempotence).
        report_id = f"rep_{command['scan_id']}"
        sections = [
            self._score_section(command),
            self._top_five_section(command),
            self._correlations_section(command),
            self._detail_section(command),
            self._compliance_section(command),
        ]
        markdown = self._render(command, sections)
        return GenerateReportResult(report_id=report_id, markdown=markdown)

    @staticmethod
    def _render(command: GenerateReportCommand, sections: list[str]) -> str:
        title = command["title"].strip() or "Rapport d'audit hexa-sec"
        lines = [f"# {title}"]
        if command["ai_summary"].strip():
            lines.append("")
            lines.append(f"> {command['ai_summary'].strip()}")
        for section in sections:
            lines.append("")
            lines.append(section)
        return "\n".join(lines) + "\n"

    def _score_section(self, command: GenerateReportCommand) -> str:
        risk_score = RiskScore.from_value(float(command["score"]))
        lines = [
            "## 1. Score global",
            f"Score : {command['score']}/100 — {risk_score.label}",
        ]
        previous = command["previous_score"]
        if previous is not None:
            delta = command["score"] - previous
            sign = f"+{delta}" if delta >= 0 else str(delta)
            lines.append(f"Évolution vs scan précédent : {previous} → {command['score']} ({sign})")
        return "\n".join(lines)

    def _top_five_section(self, command: GenerateReportCommand) -> str:
        lines = ["## 2. Top 5 « fix first »"]
        actions = sorted(
            command["actions"],
            key=lambda action: (-action["score"], action["finding_id"]),
        )[:5]
        if not actions:
            lines.append("Aucun finding à corriger en priorité.")
            return "\n".join(lines)
        for rank, action in enumerate(actions, start=1):
            lines.append(
                f"{rank}. **{action['issue']}** ({action['severity']}, "
                f"{action['score']}/100) — {action['finding_id']}"
            )
            lines.append(f"   - Pourquoi : {action['why']}")
            lines.append(f"   - Fix : {action['fix']}")
            lines.append(f"   - Effort : {action['effort']}")
        return "\n".join(lines)

    def _correlations_section(self, command: GenerateReportCommand) -> str:
        lines = ["## 3. Corrélations"]
        correlations = [
            correlation for correlation in command["correlations"] if correlation["findings"]
        ]
        if not correlations:
            lines.append("Aucune corrélation détectée.")
            return "\n".join(lines)
        for correlation in correlations:
            proof = ", ".join(correlation["findings"])
            lines.append(
                f"- **{correlation['type']}** : {correlation['reason']} (findings : {proof})"
            )
        return "\n".join(lines)

    def _detail_section(self, command: GenerateReportCommand) -> str:
        lines = ["## 4. Détail technique"]
        findings = [
            finding
            for finding in command["findings"]
            if finding["scanner"].strip() and finding["evidence"].strip()
        ]
        if not findings:
            lines.append("Aucun finding avec preuve (scanner + évidence).")
            return "\n".join(lines)
        for finding in findings:
            lines.append(
                f"- **{finding['title']}** ({finding['severity']}) — {finding['finding_id']}"
            )
            lines.append(f"  - Scanner : {finding['scanner']}")
            lines.append(f"  - Évidence : {finding['evidence']}")
        return "\n".join(lines)

    def _compliance_section(self, command: GenerateReportCommand) -> str:
        lines = ["## 5. Conformité"]
        by_scope = {
            ComplianceScope(record["scope"]).value: record for record in command["compliance"]
        }
        if not by_scope:
            lines.append("Aucun score de conformité disponible.")
            return "\n".join(lines)
        for scope in _FRAMEWORK_ORDER:
            if scope.value in by_scope:
                record = by_scope[scope.value]
                lines.append(f"- {record['scope']} : {record['value']}/100")
        return "\n".join(lines)
