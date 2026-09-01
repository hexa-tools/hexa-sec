"""Tests for DockerImagePolicy (Docker runtime bootstrap)."""

from __future__ import annotations

from hexa_sec.adapters.secondary.execution.docker_image_policy import DockerImagePolicy
from hexa_sec.application.ports.driven.image_policy import ImageRef


def _inventory() -> dict[str, dict[str, object]]:
    return {
        "network_port_discovery": {"image": "instrumentisto/nmap", "digest": "sha256:abc"},
        "web_cve_templates_nuclei": {"image": "projectdiscovery/nuclei"},
    }


def test_resolve_known_tool() -> None:
    policy = DockerImagePolicy(_inventory())
    ref = policy.resolve("network_port_discovery")
    assert ref is not None
    assert ref.image == "instrumentisto/nmap"
    assert ref.digest == "sha256:abc"


def test_resolve_unknown_tool_returns_none() -> None:
    policy = DockerImagePolicy(_inventory())
    assert policy.resolve("does-not-exist") is None


def test_resolve_without_digest() -> None:
    policy = DockerImagePolicy(_inventory())
    ref = policy.resolve("web_cve_templates_nuclei")
    assert ref is not None
    assert ref.digest is None


def test_inventory_without_image_is_unavailable() -> None:
    policy = DockerImagePolicy({"some_tool": {"description": "no image"}})
    assert policy.resolve("some_tool") is None


def test_from_scanners_flattens_families(tmp_path: object) -> None:
    import yaml
    from pathlib import Path

    path = Path(tmp_path) / "scanners.yml"
    path.write_text(
        "families:\n  network:\n    tools:\n      - name: network_port_discovery\n        image: instrumentisto/nmap\n",
        encoding="utf-8",
    )
    policy = DockerImagePolicy.from_scanners(path)
    ref = policy.resolve("network_port_discovery")
    assert ref is not None
    assert ref.image == "instrumentisto/nmap"


def test_flatten_ignores_doc_without_families(tmp_path: object) -> None:
    import yaml
    from pathlib import Path

    path = Path(tmp_path) / "scanners.yml"
    path.write_text("unrelated: true\n", encoding="utf-8")
    policy = DockerImagePolicy.from_scanners(path)
    assert policy.resolve("none") is None


def test_flatten_is_robust_to_malformed_docs() -> None:
    from hexa_sec.adapters.secondary.execution.docker_image_policy import DockerImagePolicy

    flatten = DockerImagePolicy._flatten
    assert flatten({"families": "not-dict"}) == {}
    assert flatten({"families": {"x": "not-dict"}}) == {}
    assert flatten({"families": {"x": {"tools": "not-a-list"}}}) == {}
    assert flatten({"families": {"x": {"tools": ["not-a-dict"]}}}) == {}
    assert flatten({"families": {"x": {"tools": [{"name": 123, "image": "img"}]}}}) == {}
    assert flatten({"families": {"x": {"tools": [{"name": "only-name"}]}}}) == {
        "only-name": {"image": None, "digest": None}
    }


def test_skip_non_string_image_and_digest() -> None:
    from hexa_sec.adapters.secondary.execution.docker_image_policy import DockerImagePolicy

    policy = DockerImagePolicy({"t": {"image": 123, "digest": 456}})
    assert policy.resolve("t") is None
    ref = DockerImagePolicy({"t": {"image": "nmap:7", "digest": 456}}).resolve("t")
    assert ref is not None
    assert ref.digest is None
