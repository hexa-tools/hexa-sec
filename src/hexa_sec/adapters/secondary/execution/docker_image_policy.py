"""Docker image policy — resolves a tool to an approved image (deny-by-default).

The LLM never chooses an image: adapters ask the policy, which reflects
``packs/scanners.yml`` (the source of truth). Unknown tools return ``None``.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import yaml

from hexa_sec.application.ports.driven.image_policy import ImagePolicy, ImageRef


class DockerImagePolicy(ImagePolicy):
    """Resolve tool names to approved images from an agent inventory."""

    def __init__(self, inventory: Mapping[str, Mapping[str, object]]) -> None:
        self._refs: dict[str, ImageRef] = {}
        for tool, entry in inventory.items():
            image = entry.get("image")
            if isinstance(image, str) and image.strip():
                digest = entry.get("digest")
                self._refs[tool] = ImageRef(
                    image=image,
                    digest=digest if isinstance(digest, str) else None,
                )

    def resolve(self, tool: str) -> ImageRef | None:
        return self._refs.get(tool)

    @classmethod
    def from_scanners(cls, path: Path) -> DockerImagePolicy:
        """Build the policy from ``packs/scanners.yml`` (flattened family tools)."""
        inventory = cls._flatten(yaml.safe_load(path.read_text(encoding="utf-8")))
        return cls(inventory)

    @staticmethod
    def _flatten(doc: Mapping[str, object]) -> dict[str, dict[str, object]]:
        flat: dict[str, dict[str, object]] = {}
        families = doc.get("families")
        if not isinstance(families, dict):
            return flat
        for family in families.values():
            if not isinstance(family, dict):
                continue
            tools = family.get("tools", [])
            if not isinstance(tools, list):
                continue
            for tool in tools:
                if not isinstance(tool, dict):
                    continue
                name = tool.get("name")
                if isinstance(name, str):
                    flat[name] = {
                        "image": tool.get("image"),
                        "digest": tool.get("digest"),
                    }
        return flat
