"""CodeLocation — where a risky pattern was found (context: code_risk, SEC-14).

The location (file + line) is part of the proof: without it a finding is
speculation. The file must be non-empty and the line is 1-based (``line >= 1``).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CodeLocation:
    """A file/line position in the codebase."""

    file: str
    line: int

    def __post_init__(self) -> None:
        if not self.file or not self.file.strip():
            raise ValueError("code location file cannot be empty")
        if self.line < 1:
            raise ValueError("code location line must be >= 1")
        object.__setattr__(self, "file", self.file.strip())
