"""PackManifest — the pack.yaml manifest (context: pack_config)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PackManifest:
    """Describes the pack entrypoint. hexa-sec is an MCP pack."""

    name: str
    entrypoint: str

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("pack name cannot be empty")

    def is_mcp(self) -> bool:
        return self.entrypoint.startswith("mcp://")
