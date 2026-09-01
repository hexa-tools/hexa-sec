"""env_contract — deterministic validation of the .env contract (SEC-2).

The template ``.env.example`` is the source of truth: every allowed key, its
documented purpose, and which are required. This module enforces:

  template (always, safe in CI):
    - every key is documented (has a comment)
    - every value is empty (no secret is ever committed)
    - no duplicate keys
    - keys are grouped under a ``## SECTION`` header

  env (only when a local ``.env`` exists):
    - no unknown key (reject keys not in the template)
    - for every SECTION that is "active" (any of its keys present), each
      ``# REQUIRED`` key must be present and non-empty

Secrets are never read nor printed — only presence/emptiness is checked.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

_SECTION_RE = re.compile(r"^#{2,}\s+([A-Z0-9_\-]+)\s*$")
_KEY_RE = re.compile(r"^([A-Z][A-Z0-9_]*)=(.*)$")
_REQUIRED_RE = re.compile(r"REQUIRED", re.IGNORECASE)


@dataclass(frozen=True)
class KeySpec:
    """One contract key, its section, and its documentation."""

    section: str
    key: str
    value: str
    comment: str
    required: bool


def parse_template(text: str) -> list[KeySpec]:
    """Parse the .env.example content into ordered keys grouped by section."""
    specs: list[KeySpec] = []
    section = "ROOT"

    for line in text.splitlines():
        stripped = line.strip()

        header = _SECTION_RE.match(stripped)
        if header:
            section = header.group(1)
            continue

        match = _KEY_RE.match(stripped)
        if not match:
            continue

        key, rest = match.group(1), match.group(2)
        comment = ""
        value = rest
        if "#" in rest:
            value, comment = rest.split("#", 1)
        value = value.strip()
        comment = comment.strip()

        specs.append(
            KeySpec(
                section=section,
                key=key,
                value=value,
                comment=comment,
                required=_REQUIRED_RE.search(comment) is not None,
            )
        )

    return specs


def validate_template(specs: list[KeySpec]) -> list[str]:
    """Return violations of the template contract (documented + empty).

    A key may legitimately appear in several sections (cross-project shared
    vars), so duplicates are only flagged within the *same* section.
    """
    violations: list[str] = []
    seen: set[tuple[str, str]] = set()

    for spec in specs:
        marker = (spec.section, spec.key)
        if marker in seen:
            violations.append(f"duplicate key: {spec.key} in section {spec.section}")
        seen.add(marker)
        if not spec.comment:
            violations.append(f"undocumented key: {spec.key}")
        if spec.value:
            violations.append(f"non-empty secret in template: {spec.key}")

    return violations


def parse_env(text: str) -> dict[str, str]:
    """Parse a .env file into a key -> value map (ignores comments/blank)."""
    env: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = _KEY_RE.match(stripped)
        if not match:
            continue
        key, rest = match.group(1), match.group(2)
        env[key] = rest.split("#", 1)[0].strip()
    return env


def validate_env(env: dict[str, str], specs: list[KeySpec]) -> list[str]:
    """Return violations of the .env against the template contract."""
    violations: list[str] = []
    allowed = {spec.key for spec in specs}

    for key in env:
        if key not in allowed:
            violations.append(f"unknown key in .env: {key}")

    active_sections: set[str] = set()
    for spec in specs:
        if spec.key in env:
            active_sections.add(spec.section)

    for spec in specs:
        if spec.required and spec.section in active_sections:
            value = env.get(spec.key)
            if value is None or not value.strip():
                violations.append(f"missing required key: {spec.key}")

    return violations


def _load(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main(argv: list[str]) -> int:
    """Entry point — validate the template, and the .env if present."""
    root = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    template_path = root / ".env.example"
    if not template_path.exists():
        print(f"env_contract ❌ missing template: {template_path}")
        return 1

    specs = parse_template(_load(template_path))
    violations = validate_template(specs)

    env_path = root / ".env"
    if env_path.exists():
        violations += validate_env(parse_env(_load(env_path)), specs)

    for violation in violations:
        print(f"env_contract ❌ {violation}")
    if violations:
        print(f"{len(violations)} violation(s) — fix before contributing.")
        return 1
    print("env_contract ✅ .env contract valid.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv))
