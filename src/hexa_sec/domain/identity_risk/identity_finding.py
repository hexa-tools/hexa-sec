"""IdentityFinding — an identity/access issue (context: identity_risk)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IdentityFinding:
    """An AD / SSO / account exposure."""

    principal: str
    issue: str

    def __post_init__(self) -> None:
        if not self.principal:
            raise ValueError("identity finding principal cannot be empty")
        if not self.issue:
            raise ValueError("identity finding issue cannot be empty")
