"""Unit tests for scripts/update_test_badge.py."""

from __future__ import annotations

from pathlib import Path

import pytest

import update_test_badge as badge


def _readme_with(count: int) -> str:
    return (
        "# hexa-sec\n\n"
        f"[![Tests](https://img.shields.io/badge/tests-{count}_passed-brightgreen.svg)]()\n"
    )


def test_render_badge_url() -> None:
    assert (
        badge.render_badge_url(21) == "https://img.shields.io/badge/tests-21_passed-brightgreen.svg"
    )


def test_updates_badge_count(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(badge, "README_PATH", tmp_path / "README.md")
    badge.README_PATH.write_text(_readme_with(0), encoding="utf-8")
    changed = badge.update_badge(21)
    assert changed is True
    assert "tests-21_passed" in badge.README_PATH.read_text(encoding="utf-8")


def test_no_change_when_count_is_same(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(badge, "README_PATH", tmp_path / "README.md")
    badge.README_PATH.write_text(_readme_with(21), encoding="utf-8")
    changed = badge.update_badge(21)
    assert changed is False


def test_no_badge_pattern_returns_false(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(badge, "README_PATH", tmp_path / "README.md")
    badge.README_PATH.write_text("# hexa-sec\n\nNo badge here.\n", encoding="utf-8")
    changed = badge.update_badge(21)
    assert changed is False
