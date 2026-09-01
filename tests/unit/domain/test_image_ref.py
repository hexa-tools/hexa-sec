"""Tests for ImageRef (context: container_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.container_risk.image_ref import ImageRef


def test_image_ref_creation() -> None:
    image = ImageRef(repository="acme/payment", tag="1.4.2")
    assert image.qualified == "acme/payment:1.4.2"


def test_image_ref_rejects_empty_repository() -> None:
    with pytest.raises(ValueError):
        ImageRef(repository="", tag="latest")


def test_image_ref_rejects_empty_tag() -> None:
    with pytest.raises(ValueError):
        ImageRef(repository="", tag="")


def test_image_ref_defaults_tag_to_latest() -> None:
    assert ImageRef(repository="acme/payment").qualified == "acme/payment:latest"
    assert ImageRef(repository="acme/payment", tag="   ").qualified == "acme/payment:latest"


def test_image_ref_digest() -> None:
    image = ImageRef(repository="acme/payment", tag="1.4.2", digest="sha256:abc")
    assert image.qualified == "acme/payment:1.4.2@sha256:abc"


def test_image_ref_normalizes_fields() -> None:
    image = ImageRef("  acme/payment  ", "  1.4.2  ", "  sha256:abc  ")
    assert image.repository == "acme/payment"
    assert image.tag == "1.4.2"
    assert image.digest == "sha256:abc"
