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
        if not isinstance(self.platform, MobilePlatform):
            raise ValueError("mobile finding platform must be a MobilePlatform")
        if self.secret_type is not None and not isinstance(self.secret_type, SecretType):
            raise ValueError("mobile finding secret_type must be a SecretType")
        object.__setattr__(self, "package", self.package.strip())
        object.__setattr__(self, "issue", self.issue.strip())

    def embeds_secret(self) -> bool:
        return self.secret_type is not None
