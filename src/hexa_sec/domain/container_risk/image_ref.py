"""ImageRef — a container image reference (context: container_risk).

A repository + tag (+ optional digest). Repository, tag and digest are normalized
so an image is never mis-matched in aggregation by a padding.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ImageRef:
    """A container image repository and tag."""

    repository: str
    tag: str = ""
    digest: str = ""

    def __post_init__(self) -> None:
        if not self.repository.strip():
            raise ValueError("image repository cannot be empty")
        repository = self.repository.strip()
        tag = self.tag.strip() or "latest"
        object.__setattr__(self, "repository", repository)
        object.__setattr__(self, "tag", tag)
        object.__setattr__(self, "digest", self.digest.strip())

    @property
    def qualified(self) -> str:
        """The ``repository:tag`` reference, with ``@digest`` when present."""
        qualified = f"{self.repository}:{self.tag}"
        if self.digest:
            return f"{qualified}@{self.digest}"
        return qualified
