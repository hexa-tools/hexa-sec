"""License + LicenseRisk — the legal risk of a dependency (context: dependency_risk, SEC-13).

A ``License`` is a license identifier; a ``LicenseRisk`` classifies it: a
permissive license (MIT, Apache, BSD...) is low risk, a copyleft license
(GPL/AGPL/LGPL) is high, and an unknown or absent license is UNKNOWN — never
guessed. Values are matched on the normalized identifier only, never invented.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

_COPYLEFT = {
    "gpl",
    "gpl-2.0",
    "gpl-3.0",
    "agpl",
    "agpl-3.0",
    "lgpl",
    "lgpl-2.1",
    "lgpl-3.0",
    "epl",
    "epl-1.0",
    "epl-2.0",
}
_PERMISSIVE = {
    "mit",
    "apache",
    "apache-2.0",
    "bsd",
    "bsd-2-clause",
    "bsd-3-clause",
    "isc",
    "mpl-2.0",
}


@dataclass(frozen=True)
class License:
    """A detected license identifier (e.g. ``MIT``, ``GPL-3.0``)."""

    identifier: str

    def __post_init__(self) -> None:
        if not self.identifier or not self.identifier.strip():
            raise ValueError("license identifier cannot be empty")
        object.__setattr__(self, "identifier", self.identifier.strip())


class LicenseRiskLevel(Enum):
    """The legal risk of a license for the consumer."""

    PERMISSIVE = "permissive"
    UNKNOWN = "unknown"
    COPYLEFT = "copyleft"

    @property
    def rank(self) -> int:
        return {
            LicenseRiskLevel.PERMISSIVE: 0,
            LicenseRiskLevel.UNKNOWN: 1,
            LicenseRiskLevel.COPYLEFT: 2,
        }[self]

    @property
    def is_risky(self) -> bool:
        """Whether the license imposes a strong legal obligation."""
        return self is LicenseRiskLevel.COPYLEFT


@dataclass(frozen=True)
class LicenseRisk:
    """A license and its derived legal risk level."""

    license: License | None
    level: LicenseRiskLevel

    @classmethod
    def for_identifier(cls, identifier: str | None) -> LicenseRisk:
        """Classify a license identifier; unknown/absent is ``UNKNOWN``.

        Never guesses a level for an unknown or missing license.
        """
        if identifier is None or not identifier.strip():
            return cls(license=None, level=LicenseRiskLevel.UNKNOWN)
        cleaned = identifier.strip().lower()
        if cleaned in _COPYLEFT:
            return cls(license=License(identifier), level=LicenseRiskLevel.COPYLEFT)
        if cleaned in _PERMISSIVE:
            return cls(license=License(identifier), level=LicenseRiskLevel.PERMISSIVE)
        return cls(license=License(identifier), level=LicenseRiskLevel.UNKNOWN)
