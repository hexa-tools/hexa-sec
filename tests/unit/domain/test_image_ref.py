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
        ImageRef(repository="acme/payment", tag="")
