"""Subdomain — a discovered hostname under a domain (context: dns_risk)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Subdomain:
    """A subdomain found during enumeration."""

    name: str
    resolved: bool = False
    wildcard: bool = False

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("subdomain name cannot be empty")
