"""ApiEndpoint — an exposed API route (context: api_risk)."""

from __future__ import annotations

from dataclasses import dataclass

HTTP_METHODS = frozenset({"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"})


@dataclass(frozen=True)
class ApiEndpoint:
    """An HTTP route and whether it requires authentication."""

    method: str
    path: str
    auth_required: bool = False

    def __post_init__(self) -> None:
        method = self.method.strip().upper()
        if not method:
            raise ValueError("api method cannot be empty")
        if method not in HTTP_METHODS:
            raise ValueError(f"unsupported http method: {method}")
        if not self.path.strip():
            raise ValueError("api path cannot be empty")
        object.__setattr__(self, "method", method)
        object.__setattr__(self, "path", self.path.strip())

    def requires_auth(self) -> bool:
        return self.auth_required
