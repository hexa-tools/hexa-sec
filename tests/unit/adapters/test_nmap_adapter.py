"""Tests for NmapAdapter (Dockerized reference tool)."""

from __future__ import annotations

import pytest

from hexa_sec.adapters.secondary.scanners.network.nmap_adapter import NmapAdapter
from hexa_sec.application.ports.driven.execution_port import (
    ExecutionMetadata,
    ExecutionStatus,
    ToolExecutionRequest,
    ToolExecutionResult,
)
from hexa_sec.application.ports.driven.image_policy import ImageRef
from hexa_sec.domain.errors import ScannerUnavailableError


class _FakeImagePolicy:
    def __init__(self, image: str | None = "instrumentisto/nmap") -> None:
        self._image = image

    def resolve(self, tool: str) -> ImageRef | None:
        return ImageRef(image=self._image, digest="sha256:abc") if self._image else None


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


def test_nmap_builds_argv_and_parses_ports() -> None:
    execution = _FakeExecution("PORT     STATE  SERVICE\n80/tcp   open   http\n22/tcp   open   ssh")
    adapter = NmapAdapter(execution, _FakeImagePolicy())
    records = adapter.scan("10.0.0.1")
    assert execution._request is not None
    assert execution._request.command == "nmap"
    assert execution._request.digest == "sha256:abc"
    assert execution._request.arguments == ("-sV", "10.0.0.1")
    assert len(records) == 2
    assert records[0]["port"] == 80
    assert records[0]["service"] == "http"


def test_nmap_returns_empty_on_no_open_ports() -> None:
    execution = _FakeExecution("All 1000 scanned ports are closed")
    assert NmapAdapter(execution, _FakeImagePolicy()).scan("10.0.0.1") == []


def test_nmap_raises_when_image_not_approved() -> None:
    with pytest.raises(ScannerUnavailableError):
        NmapAdapter(_FakeExecution(""), _FakeImagePolicy(None)).scan("10.0.0.1")
