"""IaCFileName — the path of an IaC file (context: iaac_risk, SEC-17).

The file path is part of the proof: without it a finding is speculation. An
empty path is rejected; the path is normalized (stripped).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IaCFileName:
    """A path to a Terraform/Helm/cloud-config file."""

    path: str

    def __post_init__(self) -> None:
        if not self.path or not self.path.strip():
            raise ValueError("IaC file path cannot be empty")
        object.__setattr__(self, "path", self.path.strip())
