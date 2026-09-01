"""Image policy — the approved-image gate (no arbitrary LLM-chosen images)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ImageRef:
    """An approved image reference, preferring an immutable digest."""

    image: str
    digest: str | None = None
    registry: str | None = None
    version: str | None = None

    def __post_init__(self) -> None:
        if not self.image.strip():
            raise ValueError("image cannot be empty")


class ImagePolicy(ABC):
    """Resolve a tool name to an approved image; ``None`` = not available."""

    @abstractmethod
    def resolve(self, tool: str) -> ImageRef | None:
        raise NotImplementedError  # pragma: no cover
