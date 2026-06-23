"""Shared domain primitives for GeoServer MCP."""

from geoserver_mcp.domain.catalog import (
    InstanceInventorySummary,
    LayerGroupInventoryItem,
    LayerInventoryItem,
    StoreInventoryItem,
    WorkspaceInventoryItem,
)
from geoserver_mcp.domain.enums import ReasonCode, ResponseStatus
from geoserver_mcp.domain.responses import InstanceConnectivityStatus, ToolError, ToolResponse

__all__ = [
    "InstanceInventorySummary",
    "InstanceConnectivityStatus",
    "ReasonCode",
    "ResponseStatus",
    "LayerGroupInventoryItem",
    "LayerInventoryItem",
    "StoreInventoryItem",
    "ToolError",
    "ToolResponse",
    "WorkspaceInventoryItem",
]
