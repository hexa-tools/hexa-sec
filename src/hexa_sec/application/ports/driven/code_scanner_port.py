"""CodeScannerPort — the code/secret scanner boundary (driven port)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict


class CodeFindingRecord(TypedDict):
    """A normalized code or secret finding."""

    path: str
    rule_id: str
    secret_type: str


class CodeScannerPort(ABC):
    """Run a code scanner against a repository."""

    @abstractmethod
    def scan(self, repo: str) -> list[CodeFindingRecord]:
        """Return normalized findings for ``repo``."""
        raise NotImplementedError  # pragma: no cover
