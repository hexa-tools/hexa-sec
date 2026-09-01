"""Tests for SecretStorePort (driven port)."""

from __future__ import annotations

import inspect

from hexa_sec.application.ports.driven.secret_store_port import SecretStorePort


def test_secret_store_port_is_abstract() -> None:
    assert inspect.isabstract(SecretStorePort) is True
