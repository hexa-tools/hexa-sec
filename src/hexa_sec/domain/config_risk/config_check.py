"""ConfigCheck — the check a configuration deviates against (context: config_risk, SEC-15).

The check (e.g. ``1.1.1``) identifies the specific requirement. An empty check is
rejected: without it there is no proof of a deviation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConfigCheck:
    """A specific benchmark check identifier."""

    identifier: str

    def __post_init__(self) -> None:
        if not self.identifier or not self.identifier.strip():
            raise ValueError("config check cannot be empty")
        object.__setattr__(self, "identifier", self.identifier.strip())
