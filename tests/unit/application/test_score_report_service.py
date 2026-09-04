"""Tests for ScoreReportService (US-3 deterministic scoring)."""

from __future__ import annotations

import pytest

from hexa_sec.application.ports.driving.score_report.score_report_service_port import (
    ScoreItem,
    ScoreReportCommand,
)
from hexa_sec.application.service.score_report_service import ScoreReportService


def _item(
    finding_id: str,
    severity: str,
    exploitability: float | None = None,
    exposure: float | None = None,
    impact: float | None = None,
    facility: float | None = None,
) -> ScoreItem:
    return ScoreItem(
        finding_id=finding_id,
        severity=severity,
        exploitability=exploitability,
        exposure=exposure,
        impact=impact,
        facility=facility,
    )


def _command(**overrides: object) -> ScoreReportCommand:
    defaults: dict[str, object] = {"scan_id": "scan_0001", "items": ()}
    defaults.update(overrides)
    return ScoreReportCommand(**defaults)  # type: ignore[arg-type]


def test_empty_items_scores_zero_without_failure() -> None:
    result = ScoreReportService().score(_command())
    assert result["scan_id"] == "scan_0001"
    assert result["score"] == 0
    assert result["label"] == "low"
    assert result["ordered"] == ()


def test_score_valid_components_with_coherent_label() -> None:
    result = ScoreReportService().score(
        _command(items=(_item("fnd_1", "critical", exploitability=1.0),))
    )
    score = result["ordered"][0]["score"]
    assert 0 <= score <= 100
    assert result["score"] == 100
    assert result["label"] == "critical"
    assert result["ordered"][0]["label"] == "critical"


def test_sort_descending_fix_first() -> None:
    command = _command(
        items=(
            _item("fnd_low", "low"),
            _item("fnd_crit", "critical", exploitability=1.0),
            _item("fnd_high", "high"),
        )
    )
    ordered = ScoreReportService().score(command)["ordered"]
    assert [item["finding_id"] for item in ordered] == ["fnd_crit", "fnd_high", "fnd_low"]


def test_correlate_is_deterministic() -> None:
    command = _command(items=(_item("fnd_1", "critical", exploitability=1.0),))
    assert ScoreReportService().score(command) == ScoreReportService().score(command)


def test_out_of_bounds_component_raises() -> None:
    with pytest.raises(ValueError):
        ScoreReportService().score(
            _command(items=(_item("fnd_1", "critical", exploitability=1.5),))
        )


def test_facility_raises_priority() -> None:
    without_facility = ScoreReportService().score(_command(items=(_item("fnd_1", "high"),)))[
        "score"
    ]
    with_facility = ScoreReportService().score(
        _command(items=(_item("fnd_1", "high", facility=1.0),))
    )["score"]
    assert with_facility > without_facility


# --- Category: concurrence / ordre (tie-break stable, déterministe) --------
def test_equal_scores_order_is_stable() -> None:
    high_a = _item("fnd_b", "high")
    high_b = _item("fnd_a", "high")
    first = ScoreReportService().score(_command(items=(high_a, high_b)))
    second = ScoreReportService().score(_command(items=(high_b, high_a)))
    assert first == second
    assert [item["finding_id"] for item in first["ordered"]] == ["fnd_a", "fnd_b"]


def test_all_components_contribute_to_the_score() -> None:
    full = _item("fnd_full", "critical", exploitability=1.0, exposure=0.8, impact=0.6, facility=0.3)
    without_exposure = _item(
        "fnd_partial", "critical", exploitability=1.0, impact=0.6, facility=0.3
    )
    assert ScoreReportService().score(_command(items=(full,)))["score"] == 84
    assert ScoreReportService().score(_command(items=(without_exposure,)))["score"] == 85
