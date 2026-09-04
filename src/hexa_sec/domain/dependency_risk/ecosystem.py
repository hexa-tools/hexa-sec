"""Ecosystem — the package ecosystem of a dependency (context: dependency_risk, SEC-13).

The ecosystem is what lets the report say "in this npm project, Express 4.17.1
is vulnerable". Normalization never invents an ecosystem: an unknown or
malformed label is rejected at parse time, never guessed.
"""

from __future__ import annotations

from enum import Enum


class Ecosystem(Enum):
    """A package registry / language ecosystem."""

    NPM = "npm"
    PYPI = "pypi"
    MAVEN = "maven"
    GEM = "gem"
    CARGO = "cargo"
    GOLANG = "golang"

    @classmethod
    def normalize(cls, raw: str) -> Ecosystem:
        """Map a raw label to an ``Ecosystem``; unknown values are rejected."""
        cleaned = raw.strip().lower()
        try:
            return cls(cleaned)
        except ValueError as error:
            raise ValueError(f"unknown ecosystem: {raw}") from error
