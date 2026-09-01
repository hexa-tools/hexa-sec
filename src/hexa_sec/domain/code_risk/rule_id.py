"""RuleId — the rule contract of a static-code finding (context: code_risk, SEC-14).

The rule is the contract: it identifies the risky pattern (semgrep/bandit) and
carries a short description. An empty identifier or description is rejected — the
rule must be exact, never guessed.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RuleId:
    """A static-analysis rule identifier and its short description."""

    identifier: str
    description: str

    def __post_init__(self) -> None:
        if not self.identifier or not self.identifier.strip():
            raise ValueError("rule identifier cannot be empty")
        if not self.description or not self.description.strip():
            raise ValueError("rule description cannot be empty")
        object.__setattr__(self, "identifier", self.identifier.strip())
        object.__setattr__(self, "description", self.description.strip())
