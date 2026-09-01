"""hexa_guard.py — deterministic architectural + security guard for hexa-sec.

Enforces the conventions in AGENTS.md. Run as:

    python hexa_guard.py --check        # scan src/ and exit non-zero on violation
    python hexa_guard.py --check <dir>  # scan a specific directory

Rules (R1-R9 + R12 + R15-R16 + R19-R21, the hexa-* family):
  R1  Domain purity: domain/ imports no scanner SDK, no app/adapters/infra.
  R2  Hexagonal: adapters never import domain directly (always via ports;
      only hexa_sec.domain.errors is allowed for HexaSecError subclasses).
  R3  Security: no secret material in source.
  R4  SQL: no inline SQL string in Python (lives in sql/ files).
  R5  Typing: no bare dict/list/tuple return annotations.
  R6  Exception strategy: no try/except in application/service or domain/services.
  R7  Tenant isolation: multi-tenant SQL carries a tenant filter (placeholder).
  R8  Mandate: scan_asset flow references the consent (Godfrain) context.
  R9  Docker CLI usage confined to adapters/secondary/execution/.
  R12 Typing: no ``Any`` (bare typing escapes) in typed layers.
  R15 Imports: module-level only, no function-scoped imports (DI container exempt).
  R16 Line count: files under the protected layers are capped.
  R19 Layer boundaries (AST): the domain never imports app/infra; infra imports
      the domain, never the reverse; adapters talk to domain only via errors.
  R20 Rust territory: rust/ contains no Python source.
  R21 Rust territory: hexa_sec_parse imported only in adapters/secondary/.
"""

from __future__ import annotations

import ast
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

# R12 — no "Any" typing escape (AGENTS.md: Any is forbidden outside tests/).
_ANY_IMPORT_RE = re.compile(r"from typing\s+import\b[^\n]*\bAny\b")
_ANY_ANNOTATION_RE = re.compile(r"\b(?:dict|list|tuple|set)\s*\[\s*(?:\w+\s*,\s*)*Any\s*\]|\bAny\b")

# R15 — module-level imports only. DI container wires services lazily (circular
# refs) and is deliberately exempt. Optional cloud deps may import lazily.
_LAZY_IMPORT_EXEMPT_PATHS = ("/infrastructure/bootstrap/",)
_OPTIONAL_DEP_PREFIXES = (
    "requests",
    "httpx",
    "click",
    "fastapi",
    "mcp",
    "docker",
    "yaml",
)

# R16 — max lines per file, per protected layer.
_HARD_CAP_LINES = 800
_MAX_LINES_BY_LAYER = {
    "domain/": 400,
    "application/": 400,
    "adapters/": 400,
    "infrastructure/": 400,
}

# R19 — internal layer boundaries: which hexa_sec.* sub-packages a layer may
# import. The domain never talks to the infra; the infra talks to the domain,
# never the reverse. Adapters reach the domain only through errors.
_LAYER_ALLOWED_IMPORTS = {
    "domain/": frozenset({"domain"}),
    "application/": frozenset({"domain", "application"}),
    "adapters/": frozenset({"application", "adapters", "infrastructure"}),
    "infrastructure/": frozenset({"domain", "application", "infrastructure"}),
}


def _docker_invocation(text: str) -> bool:
    return _DOCKER_CALL_RE.search(text) is not None


def _internal_layer(file_path: str) -> str | None:
    normalized = file_path.replace("\\", "/")
    for layer in ("domain/", "application/", "adapters/", "infrastructure/"):
        if f"/{layer}" in f"/{normalized}":
            return layer
    return None


def _check_layer_boundary(path: str, text: str) -> str | None:
    """R19 — AST check that internal imports respect the layer boundaries."""
    layer = _internal_layer(path)
    if layer is None:
        return None
    allowed = _LAYER_ALLOWED_IMPORTS[layer]
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        modules: list[str] = []
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
        elif isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        for module in modules:
            if not module.startswith("hexa_sec."):
                continue
            if module == "hexa_sec":
                continue
            if layer == "adapters/" and module.startswith("hexa_sec.domain.errors"):
                continue
            internal = module.split(".")[1]
            if internal not in allowed:
                return (
                    f"R19 layer boundary: '{module}' from '{path}' (layer {layer}) "
                    f"is not an allowed import"
                )
    return None


def _check_module_level_imports(path: str, text: str) -> str | None:
    """R15 — reject function-scoped imports (indented import/from lines)."""
    normalized = path.replace("\\", "/")
    if any(exempt in normalized for exempt in _LAZY_IMPORT_EXEMPT_PATHS):
        return None
    for index, line in enumerate(text.split("\n"), 1):
        if not line[:1].isspace():
            continue
        stripped = line.strip()
        if not (stripped.startswith("import ") or stripped.startswith("from ")):
            continue
        if "hexa-lazy-import" in line:
            continue
        if any(
            stripped.startswith(f"import {dep}") or stripped.startswith(f"from {dep}")
            for dep in _OPTIONAL_DEP_PREFIXES
        ):
            continue
        return f"R15 module-level imports only: '{stripped}' at line {index}"
    return None


def _check_line_limit(path: str, text: str) -> str | None:
    """R16 — enforce the per-layer line cap."""
    for layer, limit in _MAX_LINES_BY_LAYER.items():
        if f"/{layer}" in f"/{path.replace(chr(92), '/')}":
            count = len(text.split("\n"))
            if count > _HARD_CAP_LINES:
                return f"R16 god-file: '{path}' has {count} lines (hard cap 800)"
            if count > limit:
                return f"R16 line limit: '{path}' has {count} lines (limit {limit})"
            return None
    return None


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

    if _ANY_IMPORT_RE.search(text) or _ANY_ANNOTATION_RE.search(text):
        violations.append("R12 no 'Any' typing escape (use explicit types)")

    imports_violation = _check_module_level_imports(path, text)
    if imports_violation:
        violations.append(imports_violation)

    boundary_violation = _check_layer_boundary(path, text)
    if boundary_violation:
        violations.append(boundary_violation)

    line_limit_violation = _check_line_limit(path, text)
    if line_limit_violation:
        violations.append(line_limit_violation)

    normalized_py = normalized
    if "/rust/" in normalized_py and normalized_py.endswith(".py"):
        violations.append("R20 rust territory contains Python source")

    if (
        normalized_py.endswith(".py")
        and "/adapters/secondary/" not in normalized_py
        and re.search(r"import hexa_sec_parse|from hexa_sec_parse", text)
    ):
        violations.append("R21 hexa_sec_parse must be imported only in adapters/secondary/")

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
