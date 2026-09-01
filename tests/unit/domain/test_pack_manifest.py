"""Tests for PackManifest (context: pack_config)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.pack_config.pack_manifest import PackManifest


def test_pack_manifest_creation() -> None:
    manifest = PackManifest(name="hexa-sec", entrypoint="mcp://hexa-sec")
    assert manifest.entrypoint == "mcp://hexa-sec"
    assert manifest.is_mcp() is True


def test_pack_manifest_rejects_empty_name() -> None:
    with pytest.raises(ValueError):
        PackManifest(name="", entrypoint="mcp://hexa-sec")
