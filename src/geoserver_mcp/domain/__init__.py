"""Shared domain primitives for GeoServer MCP."""

from geoserver_mcp.domain.catalog import InstanceInventorySummary
from geoserver_mcp.domain.enums import ReasonCode, ResponseStatus
from geoserver_mcp.domain.responses import InstanceConnectivityStatus, ToolError, ToolResponse

__all__ = [
    "InstanceInventorySummary",
    "InstanceConnectivityStatus",
    "ReasonCode",
    "ResponseStatus",
    "ToolError",
    "ToolResponse",
]
