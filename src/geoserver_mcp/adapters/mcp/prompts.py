from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from geoserver_mcp.security import READ_ONLY_SAFETY_PROMPT


def register_read_only_safety_prompt(app: FastMCP) -> None:
    @app.prompt(
        name="read_only_safety",
        description="Explain GeoServer MCP v1 read-only safety boundaries.",
    )
    def read_only_safety() -> str:
        return READ_ONLY_SAFETY_PROMPT
