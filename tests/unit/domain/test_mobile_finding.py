"""Tests for MobileFinding (context: mobile_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.mobile_risk.mobile_finding import MobileFinding
from hexa_sec.domain.mobile_risk.mobile_platform import MobilePlatform
from hexa_sec.domain.secret_risk.secret_type import SecretType


def test_mobile_finding_creation() -> None:
    finding = MobileFinding(
        package="com.acme.app", platform=MobilePlatform.ANDROID, issue="hardcoded secret"
    )
    assert finding.platform is MobilePlatform.ANDROID
    assert finding.embeds_secret() is False


def test_mobile_finding_embeds_secret() -> None:
    finding = MobileFinding(
        package="com.acme.app",
        platform=MobilePlatform.ANDROID,
        issue="hardcoded api key",
        secret_type=SecretType.APIKEY,
    )
    assert finding.embeds_secret() is True


def test_mobile_finding_rejects_empty_package() -> None:
    with pytest.raises(ValueError):
        MobileFinding(package="", platform=MobilePlatform.IOS, issue="x")


def test_mobile_finding_rejects_empty_issue() -> None:
    with pytest.raises(ValueError):
        MobileFinding(package="com.acme.app", platform=MobilePlatform.IOS, issue="")


def test_mobile_finding_rejects_non_platform() -> None:
    with pytest.raises(ValueError):
        MobileFinding(package="com.acme.app", platform="android", issue="x")  # type: ignore[arg-type]


def test_mobile_finding_rejects_non_secret_type() -> None:
    with pytest.raises(ValueError):
        MobileFinding(
            package="com.acme.app",
            platform=MobilePlatform.ANDROID,
            issue="hardcoded api key",
            secret_type="api_key",  # type: ignore[arg-type]
        )


def test_mobile_finding_normalizes_fields() -> None:
    finding = MobileFinding(
        package="  com.acme.app  ", platform=MobilePlatform.ANDROID, issue="  hardcoded  "
    )
    assert finding.package == "com.acme.app"
    assert finding.issue == "hardcoded"
