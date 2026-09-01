"""Banner — the service banner that backs a network finding (context: network_risk).

The banner is the evidence of the exposure. Null-safe: a banner may be absent
(empty string) without inventing one — presence is decided by :attr:`is_present`,
which is what lets the inventory reject speculative findings.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Banner:
    """A raw service banner string."""

    text: str

    @property
    def is_present(self) -> bool:
        """Whether a non-blank banner was actually observed."""
        return bool(self.text.strip())

    def __post_init__(self) -> None:
        object.__setattr__(self, "text", self.text.strip())
