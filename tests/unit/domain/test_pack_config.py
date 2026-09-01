"""Tests for PackConfig (context: pack_config)."""

from __future__ import annotations

from hexa_sec.domain.pack_config.pack_config import PackConfig
from hexa_sec.domain.pack_config.pack_manifest import PackManifest
from hexa_sec.domain.pack_config.vendor_config import VendorConfig


def _manifest() -> PackManifest:
    return PackManifest(name="hexa-sec", entrypoint="mcp://hexa-sec")


def _vendor(provider: str, keys: tuple[str, ...]) -> VendorConfig:
    return VendorConfig(provider=provider, keys=keys)


def test_of_consolidates() -> None:
    config = PackConfig.of(
        _manifest(),
        (_vendor("shodan", ("SHODAN_API_KEY",)), _vendor("nvd", ("NVD_API_KEY",))),
    )
    assert config.manifest is not None
    assert config.is_mcp() is True
    assert len(config.vendor_configs) == 2
    assert "SHODAN_API_KEY" in config.declared_keys


def test_of_deduplicates_vendor_by_provider() -> None:
    config = PackConfig.of(
        _manifest(),
        (_vendor("shodan", ("A",)), _vendor("shodan", ("B",))),
    )
    assert len(config.vendor_configs) == 1


def test_of_unconfigured_is_not_mcp() -> None:
    config = PackConfig.of(None)
    assert config.manifest is None
    assert config.is_mcp() is False


def test_of_empty_vendor_configs() -> None:
    config = PackConfig.of(_manifest())
    assert config.vendor_configs == ()
    assert config.declared_keys == ()


# --- Category: stabilité / déterminisme (union des clés, ordre-indépendant) ---
def test_of_dedup_vendor_is_order_independent_for_keys() -> None:
    a = _vendor("shodan", ("SHODAN_API_KEY",))
    b = _vendor("shodan", ("SHODAN_SECRET",))
    first = PackConfig.of(_manifest(), (a, b))
    second = PackConfig.of(_manifest(), (b, a))
    assert first == second
    assert first.declared_keys == ("SHODAN_API_KEY", "SHODAN_SECRET")
