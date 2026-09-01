"""MobileFinding — a mobile application risk (context: mobile_risk)."""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.mobile_risk.mobile_platform import MobilePlatform
from hexa_sec.domain.secret_risk.secret_type import SecretType


@dataclass(frozen=True)
class MobileFinding:
    """A security issue in a mobile application."""

    package: str
    platform: MobilePlatform
    issue: str
    secret_type: SecretType | None = None

    def __post_init__(self) -> None:
        if not self.package.strip():
            raise ValueError("mobile package cannot be empty")
        if not self.issue.strip():
            raise ValueError("mobile issue cannot be empty")

    def embeds_secret(self) -> bool:
        return self.secret_type is not None
