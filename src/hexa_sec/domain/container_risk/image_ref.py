"""ImageRef — a container image reference (context: container_risk)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ImageRef:
    """A container image repository and tag."""

    repository: str
    tag: str

    def __post_init__(self) -> None:
        if not self.repository.strip():
            raise ValueError("image repository cannot be empty")
        if not self.tag.strip():
            raise ValueError("image tag cannot be empty")

    @property
    def qualified(self) -> str:
        return f"{self.repository}:{self.tag}"
