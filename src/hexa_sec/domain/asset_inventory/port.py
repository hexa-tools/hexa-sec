"""Port / Application / Version — the inventory value objects (context: asset_inventory).

An ``Application`` is the software detected on a port (the "service" of the
network scan). The bare word "service" is avoided as a declared name to satisfy
the ubiquitous-language guard.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Port:
    """A TCP/UDP port number."""

    number: int

    def __post_init__(self) -> None:
        if not 1 <= self.number <= 65535:
            raise ValueError("port must be between 1 and 65535")


@dataclass(frozen=True)
class Application:
    """The discovered application/service listening on a port."""

    name: str

    def __post_init__(self) -> None:
        name = self.name.strip().lower()
        if not name:
            raise ValueError("application name cannot be empty")
        object.__setattr__(self, "name", name)


@dataclass(frozen=True)
class Version:
    """A detected software version."""

    value: str

    def __post_init__(self) -> None:
        value = self.value.strip()
        if not value:
            raise ValueError("version cannot be empty")
        object.__setattr__(self, "value", value)
