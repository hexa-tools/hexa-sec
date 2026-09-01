"""Tests for the SecretRisk inventory aggregate (context: secret_risk, SEC-12)."""

from __future__ import annotations

from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.secret_risk.secret_finding import SecretFinding
from hexa_sec.domain.secret_risk.secret_risk import SecretRisk
from hexa_sec.domain.secret_risk.secret_type import SecretType


def _finding(
    asset: str = "acme/api",
    secret_type: SecretType = SecretType.TOKEN,
    evidence: str = "key: abc",
    revoked: bool = False,
) -> SecretFinding:
    return SecretFinding(
        asset=asset,
        secret_type=secret_type,
        evidence=evidence,
        revoked=revoked,
    )


def test_for_asset_consolidates_findings_same_asset() -> None:
    findings = (
        _finding(asset="acme/api", secret_type=SecretType.TOKEN, evidence="a1"),
        _finding(asset="acme/api", secret_type=SecretType.AWSKEY, evidence="a2"),
        _finding(asset="acme/api", secret_type=SecretType.CIPHERTEXT, evidence="a3"),
    )
    inventory = SecretRisk.for_asset("acme/api", findings)
    assert inventory.asset == "acme/api"
    assert len(inventory.findings) == 3
    assert inventory.sensitive_count == 2
    assert inventory.critical_count == 1


def test_for_asset_deduplicates_identical_findings() -> None:
    findings = (
        _finding(evidence="same-secret"),
        _finding(evidence="same-secret"),
    )
    inventory = SecretRisk.for_asset("acme/api", findings)
    assert len(inventory.findings) == 1


def test_for_asset_ignores_findings_of_other_asset() -> None:
    inventory = SecretRisk.for_asset("acme/api", (_finding(asset="other/repo"),))
    assert inventory.findings == ()
    assert inventory.sensitive_count == 0


def test_for_asset_keeps_revoked_finding() -> None:
    revoked = _finding(evidence="leaked-token", revoked=True)
    inventory = SecretRisk.for_asset("acme/api", (revoked,))
    assert len(inventory.findings) == 1
    assert inventory.findings[0].revoked is True


# --- Category: concurrence / ordre (dedup doit être indépendant de l'ordre) ---


def test_for_asset_dedup_prefers_revoked_variant() -> None:
    outstanding = _finding(evidence="same", revoked=False)
    recalled = _finding(evidence="same", revoked=True)
    inventory = SecretRisk.for_asset("acme/api", (outstanding, recalled))
    assert len(inventory.findings) == 1
    assert inventory.findings[0].revoked is True


def test_for_asset_dedup_order_independent_for_revoked() -> None:
    recalled = _finding(evidence="same", revoked=True)
    outstanding = _finding(evidence="same", revoked=False)
    first = SecretRisk.for_asset("acme/api", (recalled, outstanding))
    second = SecretRisk.for_asset("acme/api", (outstanding, recalled))
    assert first == second
    assert first.findings[0].revoked is True


def test_for_asset_no_findings_returns_empty_inventory() -> None:
    inventory = SecretRisk.for_asset("acme/api", ())
    assert inventory.findings == ()
    assert inventory.sensitive_count == 0
    assert inventory.critical_count == 0


def test_for_asset_is_deterministic() -> None:
    findings = (
        _finding(evidence="a", secret_type=SecretType.PRIVATEKEY),
        _finding(evidence="b", secret_type=SecretType.CIPHERTEXT),
    )
    first = SecretRisk.for_asset("acme/api", findings)
    second = SecretRisk.for_asset("acme/api", findings)
    assert first == second
    assert first.sensitive_count == second.sensitive_count
    assert first.critical_count == second.critical_count


def test_for_asset_critical_count_only_critical() -> None:
    findings = (
        _finding(evidence="k", secret_type=SecretType.PRIVATEKEY),
        _finding(evidence="h", secret_type=SecretType.TOKEN),
        _finding(evidence="l", secret_type=SecretType.CIPHERTEXT),
    )
    inventory = SecretRisk.for_asset("acme/api", findings)
    assert inventory.critical_count == 1
    assert inventory.sensitive_count == 2
    assert [f.severity.level for f in inventory.findings] == [
        Severity.CRITICAL,
        Severity.HIGH,
        Severity.LOW,
    ]
