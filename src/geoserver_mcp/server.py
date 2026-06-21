from __future__ import annotations

from typing import Any

from geoserver_mcp.adapters.mcp import Transport, create_mcp_app, run_mcp_app


def create_app(host: str = "127.0.0.1", port: int = 8000) -> Any:
    """Create the MCP app without requiring any GeoServer configuration."""
    return create_mcp_app(host=host, port=port)


def run_server(
    transport: Transport = "stdio",
    host: str = "127.0.0.1",
    port: int = 8000,
) -> None:
    run_mcp_app(transport=transport, host=host, port=port)
