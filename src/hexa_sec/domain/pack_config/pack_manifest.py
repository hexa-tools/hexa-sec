"""PackManifest — the pack.yaml manifest (context: pack_config).

Describes the pack entrypoint. hexa-sec is an MCP pack: ``is_mcp()`` is True
when the entrypoint starts with ``mcp://``. Both fields are normalized.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PackManifest:
    """Describes the pack entrypoint. hexa-sec is an MCP pack."""

    name: str
    entrypoint: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("pack name cannot be empty")
        if not self.entrypoint.strip():
            raise ValueError("pack entrypoint cannot be empty")
        object.__setattr__(self, "name", self.name.strip())
        object.__setattr__(self, "entrypoint", self.entrypoint.strip())

    def is_mcp(self) -> bool:
        return self.entrypoint.startswith("mcp://")
