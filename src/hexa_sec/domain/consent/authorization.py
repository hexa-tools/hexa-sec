"""Authorization — the client's written authorization (context: consent)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Authorization:
    """The written, signed authorization from the client."""

    authorizer: str
    scope: str
    granted_on: date
    reference: str

    def __post_init__(self) -> None:
        if not self.authorizer or not self.authorizer.strip():
            raise ValueError("authorizer cannot be empty")
        if not self.scope or not self.scope.strip():
            raise ValueError("scope cannot be empty")
