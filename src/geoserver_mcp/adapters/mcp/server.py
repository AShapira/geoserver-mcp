from __future__ import annotations

from typing import Literal

from mcp.server.fastmcp import FastMCP

from geoserver_mcp.adapters.geoserver_rest import GeoServerRestClient
from geoserver_mcp.adapters.mcp.prompts import register_read_only_safety_prompt
from geoserver_mcp.adapters.mcp.tools import (
    ClientFactory,
    register_check_instances_tool,
    register_list_catalog_tool,
)
from geoserver_mcp.config import RuntimeConfig

APP_NAME = "GeoServer MCP"
Transport = Literal["stdio", "sse", "streamable-http"]


def create_mcp_app(
    host: str = "127.0.0.1",
    port: int = 8000,
    runtime_config: RuntimeConfig | None = None,
    client_factory: ClientFactory = GeoServerRestClient,
) -> FastMCP:
    """Create the MCP SDK app without requiring GeoServer configuration."""
    app = FastMCP(
        APP_NAME,
        host=host,
        port=port,
        stateless_http=True,
        json_response=True,
    )
    register_read_only_safety_prompt(app)
    if runtime_config is not None:
        register_check_instances_tool(app, runtime_config, client_factory=client_factory)
        register_list_catalog_tool(app, runtime_config, client_factory=client_factory)
    return app


def run_mcp_app(
    transport: Transport = "stdio",
    host: str = "127.0.0.1",
    port: int = 8000,
    runtime_config: RuntimeConfig | None = None,
) -> None:
    app = create_mcp_app(host=host, port=port, runtime_config=runtime_config)
    app.run(transport=transport)
