"""Exposure — whether a port is reachable from the Internet (context: network_risk).

Internet exposure is what the ``exposure`` correlation is built on: a port
classified ``INTERNET_EXPOSED`` is visible from the outside and must be justified.
Normalization never invents a value: an unknown label is rejected.
"""

from __future__ import annotations

from enum import Enum


class Exposure(Enum):
    """Internet exposure class of a network service."""

    INTERNET_EXPOSED = "internet_exposed"
    INTERNAL_ONLY = "internal_only"

    def is_exposed(self) -> bool:
        """Whether the port is visible from outside the network."""
        return self is Exposure.INTERNET_EXPOSED

    @classmethod
    def normalize(cls, raw: str) -> Exposure:
        """Map a raw label to an ``Exposure``; unknown values are rejected.

        Accepts case/space/hyphen variations of the two canonical values and
        raises ``ValueError`` for anything else — never guesses.
        """
        cleaned = raw.strip().lower().replace(" ", "_").replace("-", "_")
        try:
            return cls(cleaned)
        except ValueError as error:
            raise ValueError(f"unknown exposure value: {raw}") from error
