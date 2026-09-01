"""Dependency and DependencyFinding — context: dependency_risk, SEC-13.

A ``Dependency`` is a third-party package pinned to a version, in an ecosystem.
A ``DependencyFinding`` links that dependency to a known CVE. The evidence is
mandatory: a CVE without proof is a speculation, rejected at construction — no
invented vulnerability.
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.dependency_risk.ecosystem import Ecosystem
from hexa_sec.domain.finding.severity import Severity


@dataclass(frozen=True)
class Dependency:
    """A third-party package and its pinned version."""

    package: str
    version: str
    ecosystem: Ecosystem

    def __post_init__(self) -> None:
        if not self.package or not self.package.strip():
            raise ValueError("dependency package cannot be empty")
        if not self.version or not self.version.strip():
            raise ValueError("dependency version cannot be empty")
        if not isinstance(self.ecosystem, Ecosystem):
            raise ValueError("dependency ecosystem must be an Ecosystem")


@dataclass(frozen=True)
class DependencyFinding:
    """A known vulnerability on a pinned dependency."""

    dependency: Dependency
    cve: str
    severity: Severity
    evidence: str

    def __post_init__(self) -> None:
        if not isinstance(self.dependency, Dependency):
            raise ValueError("dependency finding requires a Dependency")
        if not self.cve or not self.cve.strip():
            raise ValueError("dependency finding cve cannot be empty")
        if not isinstance(self.severity, Severity):
            raise ValueError("dependency finding severity must be a Severity")
        if not self.evidence or not self.evidence.strip():
            raise ValueError("dependency finding requires evidence (proof)")
