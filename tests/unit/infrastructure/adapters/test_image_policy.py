"""Tests for the image policy contract (Docker runtime bootstrap)."""

from __future__ import annotations

import pytest

from hexa_sec.application.ports.driven.image_policy import ImagePolicy, ImageRef


def test_image_ref_creation() -> None:
    ref = ImageRef(image="nmap:7", digest="sha256:abc", registry="docker.io", version="7")
    assert ref.digest == "sha256:abc"
    assert ref.registry == "docker.io"


def test_image_ref_rejects_empty_image() -> None:
    with pytest.raises(ValueError):
        ImageRef(image="")


def test_image_policy_is_abstract() -> None:
    import inspect

    assert inspect.isabstract(ImagePolicy) is True
