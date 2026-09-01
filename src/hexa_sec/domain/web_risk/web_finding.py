"""WebFinding — an OWASP-class web issue (context: web_risk)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WebFinding:
    """A web application risk (SQLi, XSS, auth, headers...)."""

    asset: str
    method: str

    def __post_init__(self) -> None:
        if not self.asset:
            raise ValueError("web finding asset cannot be empty")
        if not self.method:
            raise ValueError("web finding method cannot be empty")
