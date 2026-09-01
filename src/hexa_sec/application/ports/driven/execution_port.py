"""Execution port — the stable, Docker-agnostic tool-execution contract.

Scanner adapters build a :class:`ToolExecutionRequest` and call the port; the
Docker runtime (infrastructure) implements it. No Docker SDK is exposed here.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


class ExecutionStatus(Enum):
    """Outcome of a tool execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMED_OUT = "timed_out"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Mount:
    """An explicit host -> container filesystem mount."""

    source: str
    destination: str
    read_only: bool = False

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("mount source cannot be empty")
        if not self.destination.strip():
            raise ValueError("mount destination cannot be empty")


@dataclass(frozen=True)
class ResourceLimits:
    """Bounded resources for an execution (None = engine default)."""

    cpu: float | None = None
    memory_mb: int | None = None
    pids: int | None = None
    disk_mb: int | None = None

    def __post_init__(self) -> None:
        for name in ("cpu", "memory_mb", "pids", "disk_mb"):
            value = getattr(self, name)
            if value is not None and value < 0:
                raise ValueError(f"{name} cannot be negative")


@dataclass(frozen=True)
class ExecutionMetadata:
    """Structured, auditable metadata for one execution."""

    tool: str
    runtime: str
    image: str
    status: ExecutionStatus
    exit_code: int | None
    duration_ms: int
    execution_id: str
    policy: str | None = None


@dataclass(frozen=True)
class ToolExecutionRequest:
    """What to execute: an approved image, a command and its arguments (argv)."""

    image: str
    command: str
    tool: str = ""
    digest: str | None = None
    arguments: tuple[str, ...] = ()
    environment: dict[str, str] = field(default_factory=dict)
    mounts: tuple[Mount, ...] = ()
    network: str = "none"
    resources: ResourceLimits | None = None
    timeout: float | None = None
    execution_id: str = ""


@dataclass(frozen=True)
class ToolExecutionResult:
    """The outcome of an execution, with its audit metadata."""

    exit_code: int | None
    stdout: str
    stderr: str
    duration_ms: int
    status: ExecutionStatus
    execution_id: str
    metadata: ExecutionMetadata


class ToolExecutionPort(ABC):
    """Execute a tool request and return its result (no Docker SDK exposed)."""

    @abstractmethod
    def execute(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        raise NotImplementedError  # pragma: no cover
