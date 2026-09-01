"""Dataset contract for datasets/intent_examples.yaml (SEC-3)."""

from __future__ import annotations

from pathlib import Path

import yaml

_DATASET = Path(__file__).resolve().parents[3] / "datasets" / "intent_examples.yaml"
_INVENTORY = Path(__file__).resolve().parents[3] / "packs" / "scanners.yml"

MIN_QUESTIONS = 5


def _load(path: Path) -> dict[str, dict[str, object]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if isinstance(v, dict)}


def _scanner_names() -> set[str]:
    inventory = yaml.safe_load(_INVENTORY.read_text(encoding="utf-8"))
    return {
        tool["name"]
        for family in inventory["families"].values()
        for tool in family["tools"]
    }


def test_every_entry_is_keyed_by_exact_tool() -> None:
    for name, entry in _load(_DATASET).items():
        assert entry.get("tool") == name, f"tool mismatch for '{name}'"


def test_every_entry_has_a_description() -> None:
    for name, entry in _load(_DATASET).items():
        assert str(entry.get("description", "")).strip(), f"missing description for '{name}'"


def test_every_entry_has_at_least_five_questions() -> None:
    for name, entry in _load(_DATASET).items():
        questions = entry.get("questions", [])
        assert isinstance(questions, list) and len(questions) >= MIN_QUESTIONS, (
            f"'{name}' has fewer than {MIN_QUESTIONS} questions"
        )


def test_every_tool_is_a_registered_scanner() -> None:
    scanners = _scanner_names()
    for name in _load(_DATASET).keys():
        assert name in scanners, f"'{name}' is not a scanner in packs/scanners.yml"
