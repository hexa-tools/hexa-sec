"""Tests for GitleaksAdapter (Dockerized code/secrets tool)."""

from __future__ import annotations

import json

from hexa_sec.adapters.secondary.scanners.code.gitleaks_adapter import GitleaksAdapter
from hexa_sec.application.ports.driven.execution_port import (
    ExecutionMetadata,
    ExecutionStatus,
    ToolExecutionRequest,
    ToolExecutionResult,
)
from hexa_sec.application.ports.driven.image_policy import ImageRef


class _FakeExecution:
    def __init__(self, stdout: str) -> None:
        self._stdout = stdout
        self._request: ToolExecutionRequest | None = None

    def execute(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        self._request = request
        metadata = ExecutionMetadata(
            tool=request.tool,
            runtime="docker",
            image=request.image,
            status=ExecutionStatus.COMPLETED,
            exit_code=0,
            duration_ms=10,
            execution_id=request.execution_id,
            policy="deny-by-default",
        )
        return ToolExecutionResult(0, self._stdout, "", 10, ExecutionStatus.COMPLETED, request.execution_id, metadata)


class _FakeImagePolicy:
    def resolve(self, tool: str) -> ImageRef:
        return ImageRef(image="zricethezav/gitleaks", digest="sha256:c00b6")


def test_gitleaks_builds_request_and_parses_secrets() -> None:
    payload = json.dumps([{"File": "src/.env", "RuleID": "generic-api-key"}])
    execution = _FakeExecution(payload)
    adapter = GitleaksAdapter(execution, _FakeImagePolicy())
    records = adapter.scan("acme/repo")
    assert execution._request is not None
    assert execution._request.command == "gitleaks"
    assert execution._request.digest == "sha256:c00b6"
    assert records[0]["path"] == "src/.env"
    assert records[0]["rule_id"] == "generic-api-key"


def test_gitleaks_returns_empty_on_no_secret() -> None:
    execution = _FakeExecution("[]")
    assert GitleaksAdapter(execution, _FakeImagePolicy()).scan("acme/repo") == []


def test_gitleaks_handles_invalid_json() -> None:
    execution = _FakeExecution("not json")
    assert GitleaksAdapter(execution, _FakeImagePolicy()).scan("acme/repo") == []


def test_gitleaks_handles_malformed_items() -> None:
    execution = _FakeExecution(json.dumps(["nope", {"missing": True}, "x"]))
    assert GitleaksAdapter(execution, _FakeImagePolicy()).scan("acme/repo") == []


def test_gitleaks_raises_when_image_not_approved() -> None:
    import pytest

    from hexa_sec.domain.errors import ScannerUnavailableError

    class _NoImage:
        def resolve(self, tool: str) -> ImageRef | None:
            return None

    with pytest.raises(ScannerUnavailableError):
        GitleaksAdapter(_FakeExecution(""), _NoImage()).scan("acme/repo")
