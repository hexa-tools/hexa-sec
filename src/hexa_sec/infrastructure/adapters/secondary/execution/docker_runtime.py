"""DockerRuntime — the shared, deny-by-default Docker execution runtime.

Implements :class:`ToolExecutionPort` on top of the ``docker`` CLI via an
injectable :class:`DockerCommandRunner`. Container lifecycle (create, wait,
logs, kill, remove) is centrally managed and never duplicated in adapters.
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Sequence

from hexa_sec.application.ports.driven.execution_port import (
    ExecutionMetadata,
    ExecutionStatus,
    Mount,
    ResourceLimits,
    ToolExecutionPort,
    ToolExecutionRequest,
    ToolExecutionResult,
)
from hexa_sec.domain.errors import ScannerUnavailableError, SecurityPolicyError
from hexa_sec.infrastructure.adapters.secondary.execution.docker_command_runner import (
    DockerCommandRunner,
)

_IMAGE_OP_TIMEOUT = 180.0
_FORBIDDEN_SENSITIVE = ("/var/run/docker.sock", ".ssh", ".aws", ".env", "/etc/shadow")


class DockerRuntime(ToolExecutionPort):
    """Execute tool requests in ephemeral, resource-bounded containers."""

    def __init__(
        self,
        runner: DockerCommandRunner,
        allowed_networks: frozenset[str] = frozenset({"none", "bridge"}),
    ) -> None:
        self._runner = runner
        self._allowed_networks = allowed_networks

    def execute(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        self._validate_security(request)
        image_ref = self._image_ref(request.image, request.digest)
        self._ensure_image(image_ref)
        container = self._start(request, image_ref)
        started = time.monotonic()
        try:
            exit_code, timed_out = self._wait(container, request.timeout)
            logs = self._runner.run(["docker", "logs", container])
            stdout, stderr = logs.stdout, logs.stderr
        finally:
            self._runner.run(["docker", "rm", "-f", container])

        duration_ms = int((time.monotonic() - started) * 1000)
        status = self._status(exit_code, timed_out)
        metadata = ExecutionMetadata(
            tool=request.tool,
            runtime="docker",
            image=image_ref,
            status=status,
            exit_code=exit_code,
            duration_ms=duration_ms,
            execution_id=request.execution_id,
            policy="deny-by-default",
        )
        return ToolExecutionResult(
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration_ms=duration_ms,
            status=status,
            execution_id=request.execution_id,
            metadata=metadata,
        )

    def _start(self, request: ToolExecutionRequest, image_ref: str) -> str:
        name = f"hexa-sec-{request.execution_id or uuid.uuid4().hex[:8]}"
        result = self._runner.run(
            self._run_command(request, name, image_ref), timeout=_IMAGE_OP_TIMEOUT
        )
        if result.returncode != 0:
            raise SecurityPolicyError(f"container start failed: {result.stderr.strip()}")
        return result.stdout.strip()

    def _wait(self, container: str, timeout: float | None) -> tuple[int, bool]:
        wait = self._runner.run(["docker", "wait", container], timeout=timeout)
        if wait.timed_out:
            self._runner.run(["docker", "kill", container])
            self._runner.run(["docker", "kill", "-9", container])
            return -9, True
        return wait.returncode, False

    def _ensure_image(self, image_ref: str) -> None:
        if (
            self._runner.run(
                ["docker", "image", "inspect", image_ref], timeout=_IMAGE_OP_TIMEOUT
            ).returncode
            != 0
        ):
            pull = self._runner.run(["docker", "pull", image_ref], timeout=_IMAGE_OP_TIMEOUT)
            if pull.returncode != 0:
                raise ScannerUnavailableError(
                    f"image pull failed for {image_ref}: {pull.stderr.strip()}"
                )

    def _run_command(self, request: ToolExecutionRequest, name: str, image_ref: str) -> list[str]:
        command = ["docker", "run", "-d", "--name", name, "--network", request.network]
        command += self._resource_flags(request.resources)
        command += self._mount_flags(request.mounts)
        for key, value in request.environment.items():
            command += ["-e", f"{key}={value}"]
        command += [image_ref, request.command, *request.arguments]
        return command

    @staticmethod
    def _resource_flags(resources: ResourceLimits | None) -> list[str]:
        flags: list[str] = []
        if resources is None:
            return flags
        if resources.memory_mb:
            flags += ["--memory", f"{resources.memory_mb}m"]
        if resources.cpu:
            flags += ["--cpus", f"{resources.cpu}"]
        if resources.pids:
            flags += ["--pids-limit", str(resources.pids)]
        if resources.disk_mb:
            flags += ["--storage-opt", f"size={resources.disk_mb}M"]
        return flags

    @staticmethod
    def _mount_flags(mounts: Sequence[Mount]) -> list[str]:
        flags: list[str] = []
        for mount in mounts:
            mode = "readonly" if mount.read_only else "rw"
            flags += ["--mount", f"type=bind,src={mount.source},dst={mount.destination},{mode}"]
        return flags

    @staticmethod
    def _status(exit_code: int, timed_out: bool) -> ExecutionStatus:
        if timed_out:
            return ExecutionStatus.TIMED_OUT
        if exit_code == 0:
            return ExecutionStatus.COMPLETED
        return ExecutionStatus.FAILED

    @staticmethod
    def _image_ref(image: str, digest: str | None) -> str:
        if not digest:
            raise SecurityPolicyError(f"immutable digest required for '{image}' (no :latest)")
        return f"{image}@{digest}"

    def _validate_security(self, request: ToolExecutionRequest) -> None:
        if request.network not in self._allowed_networks:
            raise SecurityPolicyError(f"network mode '{request.network}' is not allowed")
        for mount in request.mounts:
            if any(token in mount.source for token in _FORBIDDEN_SENSITIVE):
                raise SecurityPolicyError(
                    f"mount of sensitive host path '{mount.source}' is denied"
                )
