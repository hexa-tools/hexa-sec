"""Docker command runner — the injectable boundary over the ``docker`` CLI.

The runtime executes ``docker`` subcommands through a runner so unit tests mock
the runner (behavior-first) rather than the raw subprocess/SDK. Commands are
always argv sequences — never shell-concatenated strings.
"""

from __future__ import annotations

import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CommandResult:
    """The result of one docker CLI invocation."""

    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False


class DockerCommandRunner(Protocol):
    """Run a docker argv sequence, honoring an optional timeout."""

    def run(self, command: Sequence[str], timeout: float | None = None) -> CommandResult:
        raise NotImplementedError  # pragma: no cover


class CliDockerCommandRunner:
    """Default runner: the ``docker`` CLI via subprocess (argv, no shell)."""

    def run(self, command: Sequence[str], timeout: float | None = None) -> CommandResult:
        try:
            process = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
            return CommandResult(process.returncode, process.stdout, process.stderr)
        except subprocess.TimeoutExpired as error:
            return CommandResult(-1, _text(error.stdout), _text(error.stderr), timed_out=True)


def _text(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return str(value) if value is not None else ""
