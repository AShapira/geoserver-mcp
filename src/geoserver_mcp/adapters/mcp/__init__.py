"""MCP SDK adapter boundary."""

from geoserver_mcp.adapters.mcp.server import APP_NAME, Transport, create_mcp_app, run_mcp_app

__all__ = ["APP_NAME", "Transport", "create_mcp_app", "run_mcp_app"]
