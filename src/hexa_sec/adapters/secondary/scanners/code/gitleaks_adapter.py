"""GitleaksAdapter — a Dockerized code/secrets tool (context: code)."""

from __future__ import annotations

import json

from hexa_sec.application.ports.driven.code_scanner_port import CodeFindingRecord, CodeScannerPort
from hexa_sec.application.ports.driven.execution_port import (
    ResourceLimits,
    ToolExecutionPort,
    ToolExecutionRequest,
)
from hexa_sec.application.ports.driven.image_policy import ImagePolicy
from hexa_sec.domain.errors import ScannerUnavailableError

_TOOL = "code_git_secrets_scan"


class GitleaksAdapter(CodeScannerPort):
    """Run ``gitleaks detect`` via the shared Docker runtime and parse JSON."""

    def __init__(self, execution: ToolExecutionPort, image_policy: ImagePolicy) -> None:
        self._execution = execution
        self._image_policy = image_policy

    def scan(self, repo: str) -> list[CodeFindingRecord]:
        image = self._image_policy.resolve(_TOOL)
        if image is None:
            raise ScannerUnavailableError("gitleaks image is not approved")
        request = ToolExecutionRequest(
            image=image.image,
            digest=image.digest,
            command="gitleaks",
            tool=_TOOL,
            arguments=("detect", "--source", repo, "--report-format", "json", "--report-path", "-"),
            network="none",
            resources=ResourceLimits(memory_mb=512, pids=256),
            timeout=180.0,
            execution_id=f"gitleaks-{repo}",
        )
        result = self._execution.execute(request)
        return self._parse(result.stdout)

    @staticmethod
    def _parse(output: str) -> list[CodeFindingRecord]:
        records: list[CodeFindingRecord] = []
        try:
            items = json.loads(output)
        except json.JSONDecodeError:
            return records
        if not isinstance(items, list):
            return records
        for item in items:
            if not isinstance(item, dict):
                continue
            rule_id = item.get("RuleID")
            if not isinstance(rule_id, str) or not rule_id:
                continue
            records.append(
                CodeFindingRecord(
                    path=str(item.get("File", "")),
                    rule_id=rule_id,
                    secret_type="api_key",
                )
            )
        return records
