"""Scanner adapter factory — one adapter per tool, behind the execution port."""

from __future__ import annotations

from hexa_sec.adapters.secondary.scanners.code.gitleaks_adapter import GitleaksAdapter
from hexa_sec.adapters.secondary.scanners.network.nmap_adapter import NmapAdapter
from hexa_sec.adapters.secondary.scanners.web.nuclei_adapter import NucleiAdapter
from hexa_sec.application.ports.driven.execution_port import ToolExecutionPort
from hexa_sec.application.ports.driven.image_policy import ImagePolicy
from hexa_sec.domain.errors import ScannerUnavailableError

_REGISTRY: dict[str, type] = {
    "network_port_discovery": NmapAdapter,
    "web_cve_templates_nuclei": NucleiAdapter,
    "code_git_secrets_scan": GitleaksAdapter,
}


def create_scanner_adapter(
    tool: str,
    execution: ToolExecutionPort,
    image_policy: ImagePolicy,
) -> object:
    """Return the adapter for ``tool`` wired to the shared execution port."""
    adapter_type = _REGISTRY.get(tool)
    if adapter_type is None:
        raise ScannerUnavailableError(f"no adapter registered for tool: {tool}")
    return adapter_type(execution, image_policy)
