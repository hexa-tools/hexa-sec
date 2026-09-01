"""AssetType — the kind of asset under audit (context: asset)."""

from __future__ import annotations

from enum import Enum


class AssetType(Enum):
    """Classification of an audited asset."""

    HOST = "host"
    WEB_APP = "web_app"
    REPO = "repo"
    CLOUD = "cloud"
    MOBILE = "mobile"
    CONTAINER = "container"
    IDENTITY = "identity"
