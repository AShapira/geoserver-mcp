from __future__ import annotations

from typing import Literal

from mcp.server.fastmcp import FastMCP

APP_NAME = "GeoServer MCP"
Transport = Literal["stdio", "sse", "streamable-http"]


def create_mcp_app(host: str = "127.0.0.1", port: int = 8000) -> FastMCP:
    """Create the MCP SDK app without requiring GeoServer configuration."""
    return FastMCP(
        APP_NAME,
        host=host,
        port=port,
        stateless_http=True,
        json_response=True,
    )


def run_mcp_app(
    transport: Transport = "stdio",
    host: str = "127.0.0.1",
    port: int = 8000,
) -> None:
    app = create_mcp_app(host=host, port=port)
    app.run(transport=transport)
