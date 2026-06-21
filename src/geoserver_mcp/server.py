from __future__ import annotations

from typing import Any

from geoserver_mcp.adapters.mcp import Transport, create_mcp_app, run_mcp_app
from geoserver_mcp.config import RuntimeConfig


def create_app(
    host: str = "127.0.0.1",
    port: int = 8000,
    runtime_config: RuntimeConfig | None = None,
) -> Any:
    """Create the MCP app without requiring any GeoServer configuration."""
    return create_mcp_app(host=host, port=port, runtime_config=runtime_config)


def run_server(
    transport: Transport = "stdio",
    host: str = "127.0.0.1",
    port: int = 8000,
    runtime_config: RuntimeConfig | None = None,
) -> None:
    run_mcp_app(transport=transport, host=host, port=port, runtime_config=runtime_config)
