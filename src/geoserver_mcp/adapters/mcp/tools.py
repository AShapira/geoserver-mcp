from __future__ import annotations

from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from geoserver_mcp.config import RuntimeConfig, RuntimeInstanceConfig
from geoserver_mcp.domain import ReasonCode, ResponseStatus, ToolError, ToolResponse
from geoserver_mcp.services.instance_service import ConnectivityClient, check_instances
from geoserver_mcp.services.inventory_service import list_instance_inventory

ClientFactory = Callable[[RuntimeInstanceConfig], ConnectivityClient]


def register_check_instances_tool(
    app: FastMCP,
    runtime_config: RuntimeConfig,
    *,
    client_factory: ClientFactory,
) -> None:
    @app.tool(name="check_instances")
    async def check_instances_tool() -> dict[str, object]:
        response = await check_instances(runtime_config, client_factory=client_factory)
        return response.model_dump(mode="json")


def register_list_catalog_tool(
    app: FastMCP,
    runtime_config: RuntimeConfig,
    *,
    client_factory: ClientFactory,
) -> None:
    @app.tool(name="list_catalog")
    async def list_catalog_tool(resource_types: list[str] | None = None) -> dict[str, object]:
        requested_resource_types = resource_types or ["instances"]
        if requested_resource_types != ["instances"]:
            response = ToolResponse(
                status=ResponseStatus.FAILED,
                errors=[
                    ToolError(
                        reason_code=ReasonCode.UNSUPPORTED_ENDPOINT,
                        message="only resource_types=['instances'] is supported in this story",
                    )
                ],
                metadata={"tool": "list_catalog", "resource_types": requested_resource_types},
            )
            return response.model_dump(mode="json")
        response = await list_instance_inventory(
            runtime_config,
            client_factory=client_factory,
        )
        return response.model_dump(mode="json")
