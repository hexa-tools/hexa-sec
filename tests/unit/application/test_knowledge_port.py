"""Tests for KnowledgePort (driven port)."""

from __future__ import annotations

import inspect

from hexa_sec.application.ports.driven.knowledge_port import KnowledgePort


def test_knowledge_port_is_abstract() -> None:
    assert inspect.isabstract(KnowledgePort) is True
