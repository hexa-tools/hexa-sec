"""Tests for ScanAssetService (US-1 orchestration)."""

from __future__ import annotations

from datetime import date

import pytest

from hexa_sec.application.ports.driven.audit_trail_port import AuditRecord, AuditTrailPort
from hexa_sec.application.ports.driven.code_scanner_port import CodeScannerPort
from hexa_sec.application.ports.driven.mandate_repository_port import MandateRepositoryPort
from hexa_sec.application.ports.driven.network_scanner_port import NetworkScannerPort
from hexa_sec.application.ports.driven.web_scanner_port import WebScannerPort
from hexa_sec.application.ports.driving.scan_asset.scan_asset_service_port import ScanAssetCommand
from hexa_sec.application.service.scan_asset_service import ScanAssetService
from hexa_sec.domain.consent.mandate import Mandate, MandateId, MandateLevel
from hexa_sec.domain.errors import (
    MandateLevelError,
    MandateNotFoundError,
    MandateScopeError,
    ScanConfigurationError,
    ScannerUnavailableError,
)


def _mandate(
    targets: tuple[str, ...] = ("10.0.0.1",),
    level: MandateLevel = MandateLevel.STANDARD,
) -> Mandate:
    return Mandate(
        mandate_id=MandateId("mnd_0001"),
        client="Acme Corp",
        targets=targets,
        start_date=date(2000, 1, 1),
        end_date=date(2100, 12, 31),
        level=level,
        signature="REF-2026-0001",
    )


class _WebScanner(WebScannerPort):
    def scan(self, asset: str) -> list[dict[str, str]]:
        return [{"title": "XSS", "severity": "high", "url": f"http://{asset}/x"}]


class _NetworkScanner(NetworkScannerPort):
    def scan(self, asset: str) -> list[dict[str, object]]:
        return [{"host": asset, "port": 443, "service": "https"}]


class _CodeScanner(CodeScannerPort):
    def scan(self, repo: str) -> list[dict[str, str]]:
        return [{"path": "src/app.py", "rule_id": "bandit:B101", "secret_type": "api_key"}]


class _Audit(AuditTrailPort):
    def __init__(self) -> None:
        self.records: list[AuditRecord] = []

    def save_audit(self, record: AuditRecord) -> None:
        self.records.append(record)

    def load_audit(self, tenant_id: str) -> list[AuditRecord]:
        return self.records


class _Repo(MandateRepositoryPort):
    def __init__(self, mandate: Mandate | None) -> None:
        self._mandate = mandate

    def load(self, mandate_id: str) -> Mandate | None:
        return self._mandate


def _command(**overrides: object) -> ScanAssetCommand:
    defaults: dict[str, object] = {
        "asset": "10.0.0.1",
        "mandate_id": "mnd_0001",
        "vendor": "nessus",
        "tenant_id": "tnt_0001",
        "depth": "complete",
        "exclusions": (),
    }
    defaults.update(overrides)
    return ScanAssetCommand(**defaults)  # type: ignore[arg-type]


def _service(
    mandate: Mandate | None = None, repo: _Repo | None = None
) -> tuple[ScanAssetService, _Audit]:
    audit = _Audit()
    service = ScanAssetService(
        mandate_repo=repo or _Repo(mandate),
        web_scanner=_WebScanner(),
        network_scanner=_NetworkScanner(),
        code_scanner=_CodeScanner(),
        audit_trail=audit,
    )
    return service, audit


def test_scan_runs_scanners_and_traces() -> None:
    service, audit = _service(_mandate())
    result = service.scan(_command())
    assert result["scan_id"].startswith("scan_")
    assert result["status"] == "pending"
    assert result["mandate_id"] == "mnd_0001"
    assert len(result["findings"]) == 3
    assert len(audit.records) == 1
    assert audit.records[0]["scan_id"] == result["scan_id"]
    assert audit.records[0]["mandate_id"] == "mnd_0001"
    assert audit.records[0]["tenant_id"] == "tnt_0001"


def test_scan_mandate_not_found() -> None:
    service, _ = _service(None)
    with pytest.raises(MandateNotFoundError):
        service.scan(_command())


def test_scan_target_out_of_scope() -> None:
    service, _ = _service(_mandate(targets=("192.168.1.1",)))
    with pytest.raises(MandateScopeError):
        service.scan(_command())


def test_scan_offensive_requires_offensive_mandate() -> None:
    service, _ = _service(_mandate(level=MandateLevel.STANDARD))
    with pytest.raises(MandateLevelError):
        service.scan(_command(depth="offensive"))


def test_scan_rejects_when_no_scanner() -> None:
    service = ScanAssetService(
        mandate_repo=_Repo(_mandate()),
        web_scanner=None,
        network_scanner=None,
        code_scanner=None,
        audit_trail=_Audit(),
    )
    with pytest.raises(ScanConfigurationError):
        service.scan(_command())


def test_scan_scanner_error_propagates() -> None:
    class _Boom(WebScannerPort):
        def scan(self, asset: str) -> list[dict[str, str]]:
            raise ScannerUnavailableError("scanner down")

    service = ScanAssetService(
        mandate_repo=_Repo(_mandate()),
        web_scanner=_Boom(),
        audit_trail=_Audit(),
    )
    with pytest.raises(ScannerUnavailableError):
        service.scan(_command())


def test_scan_without_mandate_repo_is_not_found() -> None:
    service = ScanAssetService()
    with pytest.raises(MandateNotFoundError):
        service.scan(_command())


def test_scan_without_audit_trail_still_returns() -> None:
    service = ScanAssetService(
        mandate_repo=_Repo(_mandate()),
        web_scanner=_WebScanner(),
        audit_trail=None,
    )
    result = service.scan(_command())
    assert result["scan_id"].startswith("scan_")
    assert len(result["findings"]) == 1


def test_scan_with_single_scanner_skips_others() -> None:
    service = ScanAssetService(
        mandate_repo=_Repo(_mandate()),
        web_scanner=_WebScanner(),
        audit_trail=_Audit(),
    )
    result = service.scan(_command())
    assert len(result["findings"]) == 1
    assert result["findings"][0]["title"] == "XSS"


def test_scan_without_web_scanner() -> None:
    service = ScanAssetService(
        mandate_repo=_Repo(_mandate()),
        network_scanner=_NetworkScanner(),
        audit_trail=_Audit(),
    )
    result = service.scan(_command())
    assert len(result["findings"]) == 1
    assert result["findings"][0]["port"] == 443


def test_scan_refuses_excluded_asset_without_calling_scanner() -> None:
    calls: list[str] = []

    class _SpyScanner(WebScannerPort):
        def scan(self, asset: str) -> list[dict[str, str]]:
            calls.append(asset)
            return [{"title": "XSS", "severity": "high", "url": f"http://{asset}"}]

    service = ScanAssetService(
        mandate_repo=_Repo(_mandate()),
        web_scanner=_SpyScanner(),
        code_scanner=_CodeScanner(),
        audit_trail=_Audit(),
    )
    with pytest.raises(ValueError):
        service.scan(_command(exclusions=("10.0.0.1",)))
    assert calls == []
