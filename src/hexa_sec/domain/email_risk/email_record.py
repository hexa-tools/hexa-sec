"""EmailRecord — the SPF/DKIM posture of an email domain (context: email_risk)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EmailRecord:
    """The anti-spoofing records published for a domain."""

    domain: str
    spf: str = ""
    dkim: str = ""

    def __post_init__(self) -> None:
        if not self.domain.strip():
            raise ValueError("email domain cannot be empty")
