"""BenchmarkId — the benchmark contract of a config finding (context: config_risk, SEC-15).

The benchmark (CIS, ISO, NIST) is the contract: it identifies the standard the
deviation is measured against and carries a short description. An empty
identifier or description is rejected — the benchmark id is exact, never guessed.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkId:
    """A benchmark identifier and its short description."""

    identifier: str
    description: str

    def __post_init__(self) -> None:
        if not self.identifier or not self.identifier.strip():
            raise ValueError("benchmark identifier cannot be empty")
        if not self.description or not self.description.strip():
            raise ValueError("benchmark description cannot be empty")
        object.__setattr__(self, "identifier", self.identifier.strip())
        object.__setattr__(self, "description", self.description.strip())
