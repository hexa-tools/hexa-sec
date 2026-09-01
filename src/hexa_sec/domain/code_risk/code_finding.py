"""CodeFinding — a risky code pattern (context: code_risk)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CodeFinding:
    """A static code finding (semgrep/bandit style)."""

    path: str
    rule_id: str

    def __post_init__(self) -> None:
        if not self.rule_id:
            raise ValueError("code finding rule cannot be empty")
        if not self.path:
            raise ValueError("code finding path cannot be empty")
