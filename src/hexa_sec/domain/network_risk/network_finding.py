"""NetworkFinding — an exposed service or banner (context: network_risk)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NetworkFinding:
    """A network-level exposure."""

    host: str
    port: int
    service: str
    exposed_to_internet: bool = False

    def __post_init__(self) -> None:
        if not self.host:
            raise ValueError("network finding host cannot be empty")
        if not self.service:
            raise ValueError("network finding service cannot be empty")
        if self.port < 1:
            raise ValueError("network finding port must be between 1 and 65535")
        if self.port > 65535:
            raise ValueError("network finding port must be between 1 and 65535")
