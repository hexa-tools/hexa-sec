"""TlsFinding — a TLS/certificate issue (context: tls_risk)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TlsFinding:
    """A certificate or protocol problem."""

    host: str
    expired: bool

    def __post_init__(self) -> None:
        if not self.host:
            raise ValueError("tls finding host cannot be empty")
