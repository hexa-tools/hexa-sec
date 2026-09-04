"""Unit tests for scripts/mutation_report.py (mutation badge + summary)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import mutation_report as report


def _mutmut(killed: int = 90, total: int = 100, survived: int = 10) -> dict[str, object]:
    return {
        "killed": killed,
        "survived": survived,
        "no_tests": 0,
        "timeout": 0,
        "total": total,
    }


def _rust(caught: int = 30, total: int = 37) -> dict[str, object]:
    return {
        "caught": caught,
        "missed": total - caught,
        "timeout": 0,
        "unviable": 0,
        "total_mutants": total,
    }


def _readme_with(score: float) -> str:
    color = report._color(score)
    return (
        "# hexa-sec\n\n"
        f"[![Mutation](https://img.shields.io/badge/mutation-{score:.1f}%25-{color}.svg)]()\n"
    )


def _readme_with_language_badges() -> str:
    return (
        "# hexa-sec\n\n"
        "[![Mutation](https://img.shields.io/badge/mutation-pending-grey.svg)]()\n"
        "[![Mutation Python]"
        "(https://img.shields.io/badge/mutation--python-pending-grey.svg)]()\n"
        "[![Mutation Rust]"
        "(https://img.shields.io/badge/mutation--rust-pending-grey.svg)]()\n"
    )


def test_score_ratio_and_bounds() -> None:
    assert report._score(90, 100) == 90.0
    assert report._score(0, 100) == 0.0
    assert report._score(100, 100) == 100.0
    assert report._score(0, 0) == 0.0


def test_color_thresholds() -> None:
    assert report._color(95.0) == "brightgreen"
    assert report._color(80.0) == "yellowgreen"
    assert report._color(70.0) == "yellow"
    assert report._color(50.0) == "orange"
    assert report._color(10.0) == "red"


def test_summarize_combines_both_reports() -> None:
    summary = report.summarize(_mutmut(killed=90, total=100), _rust(caught=30, total=37))
    py = summary["python"]
    rs = summary["rust"]
    overall = summary["overall"]
    assert isinstance(py, dict) and isinstance(rs, dict) and isinstance(overall, dict)
    assert py["killed"] == 90 and py["total"] == 100
    assert rs["killed"] == 30 and rs["total"] == 37
    assert overall["killed"] == 120 and overall["total"] == 137
    assert abs(float(overall["score"]) - 87.6) < 0.1


def test_summarize_handles_missing_reports() -> None:
    summary = report.summarize(None, None)
    assert summary["python"]["enabled"] is False
    assert summary["rust"]["enabled"] is False
    assert summary["overall"]["total"] == 0


def test_write_report_creates_json(tmp_path: Path) -> None:
    target = tmp_path / "report.json"
    report.write_report({"python": {}, "rust": {}, "overall": {}}, target)
    data = json.loads(target.read_text(encoding="utf-8"))
    assert "overall" in data


def test_update_badge_updates_readme(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(_readme_with(50.0), encoding="utf-8")
    summary = report.summarize(_mutmut(90, 100), _rust(30, 37))
    changed = report.update_badge(summary, readme)
    assert changed is True
    assert "mutation-87.6" in readme.read_text(encoding="utf-8")


def test_update_badge_no_change_when_same(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    summary = report.summarize(_mutmut(90, 100), _rust(30, 37))
    score = float(summary["overall"]["score"])
    readme.write_text(_readme_with(score), encoding="utf-8")
    changed = report.update_badge(summary, readme)
    assert changed is False


def test_update_badge_missing_pattern_returns_false(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text("# hexa-sec\n\nNo mutation badge here.\n", encoding="utf-8")
    summary = report.summarize(_mutmut(90, 100), _rust(30, 37))
    changed = report.update_badge(summary, readme)
    assert changed is False


def test_no_report_lowers_badge_to_zero(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(_readme_with(50.0), encoding="utf-8")
    summary = report.summarize(None, None)
    changed = report.update_badge(summary, readme)
    assert changed is True
    assert "mutation-0.0" in readme.read_text(encoding="utf-8")


def test_update_badge_updates_overall_python_and_rust(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(_readme_with_language_badges(), encoding="utf-8")
    summary = report.summarize(_mutmut(90, 100), _rust(caught=30, total=37))
    assert report.update_badge(summary, readme) is True
    content = readme.read_text(encoding="utf-8")
    assert "badge/mutation-87.6%25-yellowgreen.svg" in content
    assert "badge/mutation--python-90.0%25-brightgreen.svg" in content
    assert "badge/mutation--rust-81.1%25-yellowgreen.svg" in content


def test_update_badge_is_idempotent_on_all_three(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(_readme_with_language_badges(), encoding="utf-8")
    summary = report.summarize(_mutmut(90, 100), _rust(caught=30, total=37))
    assert report.update_badge(summary, readme) is True
    assert report.update_badge(summary, readme) is False
