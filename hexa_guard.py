"""hexa_guard.py — deterministic architectural + security guard for hexa-sec.

Enforces the conventions in AGENTS.md. Run as:

    python hexa_guard.py --check        # scan src/ and exit non-zero on violation
    python hexa_guard.py --check <dir>  # scan a specific directory

Rules (R1-R8, the hexa-* family):
  R1  Domain purity: domain/ imports no scanner SDK, no app/adapters/infra.
  R2  Hexagonal: adapters never import domain directly (always via ports).
  R3  Security: no secret material in source.
  R4  SQL: no inline SQL string in Python (lives in sql/ files).
  R5  Typing: no bare dict/list/tuple return annotations.
  R6  Exception strategy: no try/except in application/service or domain/services.
  R7  Tenant isolation: multi-tenant SQL carries a tenant filter (placeholder).
  R8  Mandate: scan_asset flow references the consent (Godfrain) context.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_DOMAIN_MARKER = "/domain/"
_ADAPTER_MARKER = "/adapters/"
_SERVICE_MARKER = "/application/service/"
_DOMAIN_SERVICE_MARKER = "/domain/services/"

_DOMAIN_FORBIDDEN = (
    "import requests",
    "import httpx",
    "import click",
    "import fastapi",
    "import nmap",
    "import shodan",
    "import tenable",
    "from requests",
    "from httpx",
    "from fastapi",
    "from hexa_sec.application",
    "from hexa_sec.adapters",
    "from hexa_sec.infrastructure",
)

_SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
)

_INLINE_SQL_RE = re.compile(
    r"SELECT .* FROM|INSERT INTO|CREATE TABLE|UPDATE .* SET|DELETE FROM|CREATE INDEX"
)
_DOCKER_EXEC_MARKER = "/adapters/secondary/execution/"
_LOAD_SQL_MARKER = "read_text"

_BARE_ANNOTATION_RE = re.compile(r"->\s*(dict|list|tuple)\b(?!\[)")
_DOMAIN_DIRECT_RE = re.compile(r"from hexa_sec\.domain\.(?!errors)([a-z_][a-z0-9_]*)")

_TRY_RE = re.compile(r"\btry\s*:")
_EXCEPT_RE = re.compile(r"\bexcept\b")
_DOCKER_CALL_RE = re.compile(
    r'subprocess\.run\(\s*\[?"docker"|["\']docker["\']\s*,\s*["\'](?:run|pull|create|wait|logs|rm|kill)["\']|^\s*import docker\b',
    re.MULTILINE,
)


def _docker_invocation(text: str) -> bool:
    return _DOCKER_CALL_RE.search(text) is not None


def find_violations(path: str, text: str) -> list[str]:
    """Return the rule violations for a single source file."""
    normalized = path.replace("\\", "/")
    violations: list[str] = []

    if _DOMAIN_MARKER in normalized:
        for forbidden in _DOMAIN_FORBIDDEN:
            if forbidden in text:
                violations.append(f"R1 domain purity: '{forbidden}'")

    if _ADAPTER_MARKER in normalized and _DOMAIN_DIRECT_RE.search(text):
        violations.append("R2 adapter imports domain models directly (use application ports)")

    for pattern in _SECRET_PATTERNS:
        if pattern.search(text):
            violations.append("R3 possible secret material in source")
            break

    if _INLINE_SQL_RE.search(text) and _LOAD_SQL_MARKER not in text:
        violations.append("R4 inline SQL string in Python (move to sql/ files)")

    if _BARE_ANNOTATION_RE.search(text):
        violations.append("R5 bare dict/list/tuple return annotation")

    if (
        (_SERVICE_MARKER in normalized or _DOMAIN_SERVICE_MARKER in normalized)
        and _TRY_RE.search(text)
        and _EXCEPT_RE.search(text)
    ):
        violations.append("R6 try/except in a service (let HexaSecError propagate)")

    if (
        normalized.endswith("scan_asset_service.py")
        and "consent" not in text
        and "NotImplementedError" not in text
    ):
        violations.append("R8 mandate: scan_asset orchestration must check the consent context")

    if (
        normalized.endswith(".py")
        and _DOCKER_EXEC_MARKER not in normalized
        and _docker_invocation(text)
    ):
        violations.append("R9 docker CLI usage must be confined to adapters/secondary/execution/")

    return violations


def scan_directories(roots: list[Path]) -> list[tuple[str, str]]:
    """Collect (path, violation) for every Python file under the roots."""
    findings: list[tuple[str, str]] = []
    for root in roots:
        if not root.exists():
            continue
        for py_file in root.rglob("*.py"):
            if "/.venv/" in str(py_file) or "/target/" in str(py_file):
                continue
            if "__pycache__" in str(py_file) or ".git" in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding="utf-8")
            except OSError:
                continue
            for violation in find_violations(str(py_file), content):
                findings.append((str(py_file), violation))
    return findings


def main(argv: list[str]) -> int:
    """Entry point for the --check mode."""
    roots = [Path("src")]
    if len(argv) > 1 and argv[1] != "--check":
        roots = [Path(argv[1])]

    findings = scan_directories(roots)
    for path, violation in findings:
        print(f"hexa_guard ❌ {violation}  ({path})")

    if findings:
        print(f"{len(findings)} violation(s) — fix before contributing.")
        return 1
    print("hexa_guard ✅ no violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
