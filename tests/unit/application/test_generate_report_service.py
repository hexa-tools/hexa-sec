"""Tests for GenerateReportService (US-5 deterministic 5-section report)."""

from __future__ import annotations

import pytest

from hexa_sec.application.ports.driving.generate_report.generate_report_service_port import (
    GenerateReportCommand,
    ReportAction,
    ReportCompliance,
    ReportCorrelation,
    ReportFinding,
)
from hexa_sec.application.service.generate_report_service import GenerateReportService

_HEADINGS = (
    "## 1. Score global",
    "## 2. Top 5 « fix first »",
    "## 3. Corrélations",
    "## 4. Détail technique",
    "## 5. Conformité",
)


def _action(finding_id: str, score: int, severity: str = "high") -> ReportAction:
    return ReportAction(
        finding_id=finding_id,
        issue=f"Issue {finding_id}",
        why="An attacker can take over the account",
        fix="Rotate the key immediately",
        effort="5 min",
        severity=severity,
        score=score,
    )


def _finding(
    finding_id: str,
    scanner: str = "burp",
    evidence: str = "raw evidence payload",
) -> ReportFinding:
    return ReportFinding(
        finding_id=finding_id,
        title=f"Finding {finding_id}",
        severity="high",
        scanner=scanner,
        evidence=evidence,
    )


def _correlation(findings: list[str]) -> ReportCorrelation:
    return ReportCorrelation(
        type="attack-chain",
        reason="A critical CVE feeds the SQL injection on the same asset",
        findings=findings,
    )


def _compliance(scope: str, value: float) -> ReportCompliance:
    return ReportCompliance(scope=scope, value=value)


def _command(**overrides: object) -> GenerateReportCommand:
    defaults: dict[str, object] = {
        "scan_id": "scan_0001",
        "tenant_id": "tnt_0001",
        "title": "",
        "score": 62,
        "previous_score": None,
        "ai_summary": "",
        "actions": (),
        "correlations": (),
        "findings": (),
        "compliance": (),
    }
    defaults.update(overrides)
    return GenerateReportCommand(**defaults)  # type: ignore[arg-type]


def _headings(markdown: str) -> list[str]:
    return [line for line in markdown.splitlines() if line.startswith("## ")]


def test_empty_report_renders_five_sections_in_order() -> None:
    markdown = GenerateReportService().generate(_command())["markdown"]
    assert _headings(markdown) == list(_HEADINGS)
    assert "aucun finding" in markdown.lower() or "Aucun" in markdown


def test_report_defaults_title_and_gauge_label() -> None:
    markdown = GenerateReportService().generate(_command(score=72))["markdown"]
    assert "Rapport d'audit" in markdown
    assert "72/100" in markdown
    assert "high" in markdown


def test_report_shows_score_evolution_when_previous_provided() -> None:
    markdown = GenerateReportService().generate(_command(score=62, previous_score=58))["markdown"]
    assert "58" in markdown
    assert "62" in markdown
    assert "+4" in markdown


def test_report_omits_evolution_without_previous_score() -> None:
    markdown = GenerateReportService().generate(_command(previous_score=None))["markdown"]
    assert "évolution" not in markdown.lower()


def test_report_embeds_ai_summary_when_provided() -> None:
    markdown = GenerateReportService().generate(
        _command(ai_summary="Votre SI est à un niveau de risque modéré.")
    )["markdown"]
    assert "Votre SI est à un niveau de risque modéré." in markdown


def test_report_omits_ai_summary_when_empty() -> None:
    markdown = GenerateReportService().generate(_command(ai_summary=""))["markdown"]
    assert "SLM" not in markdown


def test_top_five_capped_to_five_and_sorted_by_score() -> None:
    actions = tuple(_action(f"fnd_{i}", score=i) for i in range(1, 7))
    result = GenerateReportService().generate(_command(actions=actions))
    # section 2 = the markdown between heading 2 and heading 3
    section = result["markdown"].split("## 2. Top 5 « fix first »")[1].split("## 3.")[0]
    assert "fnd_6" in section
    assert "fnd_1" not in section
    assert section.index("fnd_6") < section.index("fnd_5")


def test_top_five_less_than_five_renders_actual_count() -> None:
    actions = tuple(_action(f"fnd_{i}", score=90 - i) for i in range(3))
    result = GenerateReportService().generate(_command(actions=actions))
    section = result["markdown"].split("## 2. Top 5 « fix first »")[1].split("## 3.")[0]
    for action in actions:
        assert action["finding_id"] in section


def test_top_five_never_invents_items_when_empty() -> None:
    result = GenerateReportService().generate(_command(actions=()))
    section = result["markdown"].split("## 2. Top 5 « fix first »")[1].split("## 3.")[0]
    assert "fnd_" not in section


def test_correlation_without_findings_is_excluded() -> None:
    correlations = (_correlation(findings=[]),)
    result = GenerateReportService().generate(_command(correlations=correlations))
    section = result["markdown"].split("## 3. Corrélations")[1].split("## 4.")[0]
    assert "attack-chain" not in section


def test_correlation_with_findings_is_rendered() -> None:
    correlations = (_correlation(findings=["fnd_1", "fnd_2"]),)
    result = GenerateReportService().generate(_command(correlations=correlations))
    section = result["markdown"].split("## 3. Corrélations")[1].split("## 4.")[0]
    assert "attack-chain" in section
    assert "(findings : fnd_1, fnd_2)" in section


def test_finding_without_evidence_is_excluded_from_detail() -> None:
    findings = (_finding("fnd_1", evidence=""),)
    result = GenerateReportService().generate(_command(findings=findings))
    section = result["markdown"].split("## 4. Détail technique")[1].split("## 5.")[0]
    assert "fnd_1" not in section


def test_finding_without_scanner_is_excluded_from_detail() -> None:
    findings = (_finding("fnd_1", scanner=""),)
    result = GenerateReportService().generate(_command(findings=findings))
    section = result["markdown"].split("## 4. Détail technique")[1].split("## 5.")[0]
    assert "fnd_1" not in section


def test_finding_cites_scanner_and_evidence() -> None:
    findings = (_finding("fnd_1", scanner="burp", evidence="POST /login 200 OK"),)
    result = GenerateReportService().generate(_command(findings=findings))
    section = result["markdown"].split("## 4. Détail technique")[1].split("## 5.")[0]
    assert "burp" in section
    assert "POST /login 200 OK" in section


def test_compliance_rendered_in_framework_order() -> None:
    compliance = (
        _compliance("rgpd", 70.0),
        _compliance("iso_27001", 85.0),
        _compliance("pci_dss", 40.0),
        _compliance("nis2", 55.0),
    )
    result = GenerateReportService().generate(_command(compliance=compliance))
    section = result["markdown"].split("## 5. Conformité")[1]
    assert section.index("iso_27001") < section.index("rgpd")
    assert section.index("rgpd") < section.index("nis2")
    assert section.index("nis2") < section.index("pci_dss")
    assert "85.0" in section and "70.0" in section


def test_out_of_bounds_score_raises() -> None:
    with pytest.raises(ValueError):
        GenerateReportService().generate(_command(score=120))


def test_negative_previous_score_still_renders() -> None:
    result = GenerateReportService().generate(_command(score=40, previous_score=62))
    section = result["markdown"].split("## 1.")[1].split("## 2.")[0]
    assert "-22" in section


def test_generate_is_deterministic() -> None:
    command = _command(
        actions=(_action("fnd_a", 90), _action("fnd_b", 95)),
        findings=(_finding("fnd_a"),),
        correlations=(_correlation(["fnd_a"]),),
        compliance=(_compliance("iso_27001", 80.0),),
    )
    first = GenerateReportService().generate(command)
    second = GenerateReportService().generate(command)
    assert first == second


def test_full_report_matches_exact_markdown() -> None:
    result = GenerateReportService().generate(
        _command(
            title="Audit Acme",
            score=62,
            previous_score=58,
            ai_summary="Risque modéré.",
            actions=(
                ReportAction(
                    finding_id="fnd_1",
                    issue="Exposed API key",
                    why="Account takeover",
                    fix="Rotate",
                    effort="5 min",
                    severity="critical",
                    score=95,
                ),
            ),
            correlations=(_correlation(["fnd_1"]),),
            findings=(_finding("fnd_1", scanner="burp", evidence="POST /login 200 OK"),),
            compliance=(_compliance("iso_27001", 80.0),),
        )
    )["markdown"]
    assert result == (
        "# Audit Acme\n"
        "\n"
        "> Risque modéré.\n"
        "\n"
        "## 1. Score global\n"
        "Score : 62/100 — high\n"
        "Évolution vs scan précédent : 58 → 62 (+4)\n"
        "\n"
        "## 2. Top 5 « fix first »\n"
        "1. **Exposed API key** (critical, 95/100) — fnd_1\n"
        "   - Pourquoi : Account takeover\n"
        "   - Fix : Rotate\n"
        "   - Effort : 5 min\n"
        "\n"
        "## 3. Corrélations\n"
        "- **attack-chain** : A critical CVE feeds the SQL injection on the same asset "
        "(findings : fnd_1)\n"
        "\n"
        "## 4. Détail technique\n"
        "- **Finding fnd_1** (high) — fnd_1\n"
        "  - Scanner : burp\n"
        "  - Évidence : POST /login 200 OK\n"
        "\n"
        "## 5. Conformité\n"
        "- iso_27001 : 80.0/100\n"
    )


def test_empty_report_matches_exact_markdown() -> None:
    markdown = GenerateReportService().generate(_command(score=0))["markdown"]
    assert markdown == (
        "# Rapport d'audit hexa-sec\n"
        "\n"
        "## 1. Score global\n"
        "Score : 0/100 — low\n"
        "\n"
        "## 2. Top 5 « fix first »\n"
        "Aucun finding à corriger en priorité.\n"
        "\n"
        "## 3. Corrélations\n"
        "Aucune corrélation détectée.\n"
        "\n"
        "## 4. Détail technique\n"
        "Aucun finding avec preuve (scanner + évidence).\n"
        "\n"
        "## 5. Conformité\n"
        "Aucun score de conformité disponible.\n"
    )


def test_score_evolution_uses_plus_sign_at_zero_delta() -> None:
    result = GenerateReportService().generate(_command(score=62, previous_score=62))
    section = result["markdown"].split("## 1.")[1].split("## 2.")[0]
    assert "(+0)" in section
