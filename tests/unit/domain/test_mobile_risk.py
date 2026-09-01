"""Tests for the MobileRisk aggregate (context: mobile_risk)."""

from __future__ import annotations

from hexa_sec.domain.mobile_risk.mobile_finding import MobileFinding
from hexa_sec.domain.mobile_risk.mobile_platform import MobilePlatform
from hexa_sec.domain.mobile_risk.mobile_risk import MobileRisk
from hexa_sec.domain.secret_risk.secret_type import SecretType


def _with_secret(package: str) -> MobileFinding:
    return MobileFinding(
        package=package,
        platform=MobilePlatform.ANDROID,
        issue="hardcoded api key",
        secret_type=SecretType.APIKEY,
    )


def _plain(package: str) -> MobileFinding:
    return MobileFinding(
        package=package,
        platform=MobilePlatform.ANDROID,
        issue="unprotected cert",
    )


def test_of_consolidates_findings() -> None:
    findings = (_with_secret("com.acme.app"), _plain("com.acme.other"))
    risk = MobileRisk.of(findings)
    assert len(risk.findings) == 2
    assert risk.secret_count == 1


def test_of_deduplicates_same_package_issue() -> None:
    findings = (_with_secret("com.acme.app"), _with_secret("com.acme.app"))
    risk = MobileRisk.of(findings)
    assert len(risk.findings) == 1


def test_of_keeps_secret_embedding() -> None:
    plain = MobileFinding(
        package="com.acme.app",
        platform=MobilePlatform.ANDROID,
        issue="hardcoded api key",
    )
    secret = _with_secret("com.acme.app")
    risk = MobileRisk.of((plain, secret))
    assert len(risk.findings) == 1
    assert risk.findings[0].embeds_secret() is True


def test_of_secret_packages() -> None:
    findings = (_with_secret("com.acme.app"), _plain("com.acme.other"))
    risk = MobileRisk.of(findings)
    assert risk.secret_packages() == ("com.acme.app",)
    assert risk.secret_count == 1


def test_of_empty_is_empty() -> None:
    risk = MobileRisk.of(())
    assert risk.findings == ()
    assert risk.secret_count == 0
    assert risk.secret_packages() == ()


def test_of_is_deterministic() -> None:
    findings = (_with_secret("com.acme.app"), _plain("com.acme.other"))
    first = MobileRisk.of(findings)
    second = MobileRisk.of(findings)
    assert first == second
    assert first.secret_count == second.secret_count


# --- Category: stabilité / déterminisme (tie-break sur secret_type) --------
def test_of_dedup_deterministic_for_secret_types() -> None:
    api = MobileFinding(
        "com.acme.app", MobilePlatform.ANDROID, "hardcoded api key", SecretType.APIKEY
    )
    aws = MobileFinding(
        "com.acme.app", MobilePlatform.ANDROID, "hardcoded api key", SecretType.AWSKEY
    )
    first = MobileRisk.of((api, aws))
    second = MobileRisk.of((aws, api))
    assert first == second
    assert first.findings[0].secret_type is SecretType.AWSKEY


def test_of_order_independent() -> None:
    a = _with_secret("com.acme.app")
    b = _plain("com.acme.other")
    first = MobileRisk.of((a, b))
    second = MobileRisk.of((b, a))
    assert first == second
    assert [finding.package for finding in first.findings] == [
        finding.package for finding in second.findings
    ]
