"""Dependency — a package + version (context: dependency_risk)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Dependency:
    """A third-party package and its pinned version."""

    package: str
    version: str

    def __post_init__(self) -> None:
        if not self.package:
            raise ValueError("dependency package cannot be empty")
