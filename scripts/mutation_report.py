#!/usr/bin/env python3
"""Aggregate mutation-testing results (Python mutmut + Rust cargo-mutants).

Reads the two machine-readable reports:
- ``mutants/mutmut-cicd-stats.json`` (Python, deterministic core)
- ``rust/mutants.out/outcomes.json`` (Rust, cargo-mutants)

and writes a combined JSON summary used by CI and the README badge.

Usage:
    python scripts/mutation_report.py            # print summary table
    python scripts/mutation_report.py --badge    # also update the README badge
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MUTMUT_STATS = ROOT / "mutants" / "mutmut-cicd-stats.json"
RUST_OUTCOMES = ROOT / "rust" / "mutants.out" / "outcomes.json"
DEFAULT_REPORT = ROOT / "docs" / "mutation" / "report.json"
README_PATH = ROOT / "README.md"

# Overridable for tests; None means "derive the color from the score".
BADGE_COLOR: str | None = None

# One badge per target: "overall" (existing) + one per language. The shields
# ``--`` keeps a literal dash inside the label (mutation-python / mutation-rust).
BADGES = (
    ("overall", "mutation", r"https://img\.shields\.io/badge/mutation-(?!-)[^)\s]+"),
    ("python", "mutation--python", r"https://img\.shields\.io/badge/mutation--python-[^)\s]+"),
    ("rust", "mutation--rust", r"https://img\.shields\.io/badge/mutation--rust-[^)\s]+"),
)


def _badge_url(label: str, score: float) -> str:
    color = BADGE_COLOR if BADGE_COLOR is not None else _color(score)
    return f"https://img.shields.io/badge/{label}-{score:.1f}%25-{color}.svg"


def _load(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _score(killed: int, total: int) -> float:
    return round(100.0 * killed / total, 1) if total else 0.0


def _color(score: float) -> str:
    if score >= 90:
        return "brightgreen"
    if score >= 75:
        return "yellowgreen"
    if score >= 60:
        return "yellow"
    if score >= 40:
        return "orange"
    return "red"


def summarize(
    mutmut: dict[str, object] | None,
    rust: dict[str, object] | None,
) -> dict[str, object]:
    py: dict[str, object] = {"enabled": mutmut is not None}
    if mutmut:
        killed = int(mutmut["killed"])
        total = int(mutmut["total"])
        py.update(
            killed=killed,
            survived=int(mutmut["survived"]),
            no_tests=int(mutmut.get("no_tests", 0)),
            timeout=int(mutmut.get("timeout", 0)),
            total=total,
            score=_score(killed, total),
        )

    rs: dict[str, object] = {"enabled": rust is not None}
    if rust:
        caught = int(rust["caught"])
        total = int(rust["total_mutants"])
        rs.update(
            killed=caught,
            survived=int(rust["missed"]),
            timeout=int(rust["timeout"]),
            unviable=int(rust["unviable"]),
            total=total,
            score=_score(caught, total),
        )

    overall_total = 0
    overall_killed = 0
    if mutmut:
        overall_total += int(mutmut["total"])
        overall_killed += int(mutmut["killed"])
    if rust:
        overall_total += int(rust["total_mutants"])
        overall_killed += int(rust["caught"])

    summary: dict[str, object] = {
        "python": py,
        "rust": rs,
        "overall": {
            "total": overall_total,
            "killed": overall_killed,
            "score": _score(overall_killed, overall_total),
        },
    }
    return summary


def print_table(summary: dict[str, object]) -> None:
    for language in ("python", "rust"):
        data = summary[language]
        assert isinstance(data, dict)
        if not data.get("enabled"):
            print(f"{language}: no report found")
            continue
        print(
            f"{language}: {data['killed']}/{data['total']} killed "
            f"({data['score']}%) survived={data.get('survived', 0)} "
            f"timeout={data.get('timeout', 0)}"
        )
    overall = summary["overall"]
    assert isinstance(overall, dict)
    print(f"overall: {overall['killed']}/{overall['total']} ({overall['score']}%)")


def write_report(summary: dict[str, object], path: Path = DEFAULT_REPORT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"✅ Report written to {path}")


def update_badge(summary: dict[str, object], readme: Path = README_PATH) -> bool:
    """Update the overall + per-language mutation badges in the README.

    Returns True when at least one badge line changed; False when the README is
    already up to date, or when it contains no mutation badge at all.
    """
    content = readme.read_text(encoding="utf-8")
    found_any = any(re.search(pattern, content) for _, _, pattern in BADGES)
    new_content = content

    for name, label, pattern in BADGES:
        data = summary[name]
        assert isinstance(data, dict)
        if name == "overall":
            score = float(data["score"])
        else:
            score = float(data["score"]) if data.get("enabled") else 0.0
        new_content = re.sub(pattern, _badge_url(label, score), new_content)

    if new_content == content:
        if not found_any:
            print("⚠️  Mutation badges not found in README.md — add them first")
        else:
            print("✅ Mutation badges already up to date")
        return False

    overall = summary["overall"]
    assert isinstance(overall, dict)
    readme.write_text(new_content, encoding="utf-8")
    print(f"✅ Updated mutation badges (overall {overall['score']}%)")
    return True


if __name__ == "__main__":
    summary = summarize(_load(MUTMUT_STATS), _load(RUST_OUTCOMES))
    print_table(summary)
    write_report(summary)
    if "--badge" in sys.argv:
        update_badge(summary)
