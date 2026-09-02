"""ScanAssetService — orchestrates scanners on an asset after the mandate check (US-1).

The mandate (loi Godfrain) is verified before any scanner launches. The service
never catches — the ``Mandate*Error`` and ``Scanner*Error`` propagate (R6). Only
inbound adapters (CLI/MCP) do the final catch.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from uuid import uuid4

from hexa_sec.application.ports.driven.audit_trail_port import AuditRecord, AuditTrailPort
from hexa_sec.application.ports.driven.code_scanner_port import CodeScannerPort
from hexa_sec.application.ports.driven.mandate_repository_port import MandateRepositoryPort
from hexa_sec.application.ports.driven.network_scanner_port import NetworkScannerPort
from hexa_sec.application.ports.driven.secret_store_port import SecretStorePort
from hexa_sec.application.ports.driven.web_scanner_port import WebScannerPort
from hexa_sec.application.ports.driving.scan_asset.scan_asset_service_port import (
    FindingRecord,
    ScanAssetCommand,
    ScanAssetResult,
    ScanAssetServicePort,
)
from hexa_sec.domain.asset.asset import Asset
from hexa_sec.domain.asset.asset_type import AssetType
from hexa_sec.domain.consent.mandate import Mandate
from hexa_sec.domain.errors import MandateNotFoundError, ScanConfigurationError
from hexa_sec.domain.scan.scan import Scan, ScanId
from hexa_sec.domain.scan.scan_depth import ScanDepth
from hexa_sec.domain.scan.scan_parameters import ScanParameters


class ScanAssetService(ScanAssetServicePort):
    """Orchestrate scanners on an asset, mandate-gated."""

    def __init__(
        self,
        mandate_repo: MandateRepositoryPort | None = None,
        web_scanner: WebScannerPort | None = None,
        network_scanner: NetworkScannerPort | None = None,
        code_scanner: CodeScannerPort | None = None,
        secret_store: SecretStorePort | None = None,
        audit_trail: AuditTrailPort | None = None,
    ) -> None:
        self._mandate_repo = mandate_repo
        self._web_scanner = web_scanner
        self._network_scanner = network_scanner
        self._code_scanner = code_scanner
        self._secret_store = secret_store
        self._audit_trail = audit_trail

    def scan(self, command: ScanAssetCommand) -> ScanAssetResult:
        mandate = self._load_mandate(command["mandate_id"])
        asset = Asset(name=command["asset"], type=AssetType.HOST)
        parameters = ScanParameters(
            depth=ScanDepth(command["depth"]),
            exclusions=tuple(command["exclusions"]),
        )
        scan = Scan.create(
            ScanId(f"scan_{uuid4().hex}"),
            mandate,
            (asset,),
            (command["vendor"],),
            parameters,
        )
        started = time.perf_counter()
        findings = self._run_scanners(command["asset"])
        duration_ms = int((time.perf_counter() - started) * 1000)
        self._trace(scan, command, duration_ms)
        return ScanAssetResult(
            scan_id=scan.scan_id.value,
            status=scan.status.value,
            mandate_id=scan.mandate_id.value,
            findings=findings,
        )

    def _load_mandate(self, mandate_id: str) -> Mandate | None:
        if self._mandate_repo is None:
            raise MandateNotFoundError("no mandate repository wired")
        return self._mandate_repo.load(mandate_id)

    def _run_scanners(self, asset: str) -> list[FindingRecord]:
        if not any(
            scanner is not None
            for scanner in (self._web_scanner, self._network_scanner, self._code_scanner)
        ):
            raise ScanConfigurationError("at least one scanner port is required")
        findings: list[FindingRecord] = []
        if self._web_scanner is not None:
            findings.extend(self._web_scanner.scan(asset))
        if self._network_scanner is not None:
            findings.extend(self._network_scanner.scan(asset))
        if self._code_scanner is not None:
            findings.extend(self._code_scanner.scan(asset))
        return findings

    def _trace(self, scan: Scan, command: ScanAssetCommand, duration_ms: int) -> None:
        if self._audit_trail is None:
            return
        self._audit_trail.save_audit(
            AuditRecord(
                tenant_id=command["tenant_id"],
                entry_id=scan.scan_id.value,
                scan_id=scan.scan_id.value,
                mandate_id=scan.mandate_id.value,
                action="scan",
                actor="operator",
                image=command["vendor"],
                digest="",
                duration_ms=duration_ms,
                recorded_at=datetime.now(UTC).isoformat(),
            )
        )
