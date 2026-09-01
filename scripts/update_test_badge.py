#!/usr/bin/env python3
"""Update the tests badge in README.md with the current unit-test count.

Counts the collected pytest unit tests (dry-run, no execution) and rewrites the
badge URL in README.md. Hooked up as ``make update-badge``.

Usage:
    python scripts/update_test_badge.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README_PATH = ROOT / "README.md"
BADGE_PATTERN = re.compile(
    r"https://img\.shields\.io/badge/tests-\d+(?:%2B)?_passed-brightgreen\.svg"
)


def render_badge_url(count: int) -> str:
    """Shields.io URL for the test-count badge."""
    return f"https://img.shields.io/badge/tests-{count}_passed-brightgreen.svg"


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(args, capture_output=True, text=True, cwd=cwd)
    except FileNotFoundError:
        return None


def count_tests() -> int:
    """Unit test count via pytest --collect-only (fast, no execution)."""
    result = _run(
        [
            "poetry",
            "run",
            "pytest",
            "tests/unit",
            "-m",
            "not integration and not e2e",
            "--collect-only",
        ],
        ROOT,
    )
    if result is None:
        print("⚠️  poetry not found — skipping")
        return 0
    for line in reversed(result.stdout.splitlines()):
        match = re.search(r"(\d+) tests? collected", line)
        if match:
            return int(match.group(1))
    print("⚠️  Could not count tests")
    return 0


def update_badge(count: int) -> bool:
    """Rewrite the badge URL in README.md; return True when changed."""
    content = README_PATH.read_text(encoding="utf-8")
    new_content, n = BADGE_PATTERN.subn(render_badge_url(count), content)
    if n == 0:
        print("⚠️  Badge pattern not found in README.md — skipping update")
        return False
    if new_content == content:
        print(f"✅ Badge already up to date ({count} tests)")
        return False
    README_PATH.write_text(new_content, encoding="utf-8")
    print(f"✅ Updated README.md badge → {count} tests")
    return True


if __name__ == "__main__":
    count = count_tests()
    if count == 0:
        print("❌ Could not collect test count — aborting badge update")
        sys.exit(1)
    update_badge(count)
