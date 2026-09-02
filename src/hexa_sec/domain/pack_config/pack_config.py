"""PackConfig — the pack's declared configuration (context: pack_config).

``of`` consolidates a manifest with the vendors' declared key names (no values),
deduplicating vendors by provider. A pack that is not configured is a normal,
empty state — ``is_mcp()`` is then False (fail-closed).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from hexa_sec.domain.pack_config.pack_manifest import PackManifest
from hexa_sec.domain.pack_config.vendor_config import VendorConfig


@dataclass(frozen=True)
class PackConfig:
    """The declared configuration of the pack."""

    manifest: PackManifest | None = None
    vendor_configs: tuple[VendorConfig, ...] = ()

    @property
    def declared_keys(self) -> tuple[str, ...]:
        """All declared vendor key names, sorted and deduplicated."""
        keys = sorted({key for config in self.vendor_configs for key in config.keys})
        return tuple(keys)

    def is_mcp(self) -> bool:
        """Whether the pack is configured as an MCP pack (fail-closed)."""
        return self.manifest is not None and self.manifest.is_mcp()

    @classmethod
    def of(
        cls,
        manifest: PackManifest | None,
        vendor_configs: Iterable[VendorConfig] = (),
    ) -> PackConfig:
        """Build the config, unioning vendor keys per provider (deterministic)."""
        keys_by_provider: dict[str, set[str]] = {}
        for config in vendor_configs:
            keys_by_provider.setdefault(config.provider, set()).update(config.keys)
        merged = tuple(
            sorted(
                (
                    VendorConfig(provider=provider, keys=tuple(sorted(keys)))
                    for provider, keys in keys_by_provider.items()
                ),
                key=lambda c: c.provider,
            )
        )
        return cls(manifest=manifest, vendor_configs=merged)
