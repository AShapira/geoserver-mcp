from __future__ import annotations

from geoserver_mcp.adapters.geoserver_rest import GeoServerRestClient
from geoserver_mcp.config import RuntimeConfig
from geoserver_mcp.domain import (
    InstanceConnectivityStatus,
    InstanceInventorySummary,
    ToolError,
    ToolResponse,
)
from geoserver_mcp.services.instance_service import ClientFactory, check_instances

INSTANCE_SURFACE = "geoserver_rest:about_version"


async def list_instance_inventory(
    runtime_config: RuntimeConfig,
    *,
    client_factory: ClientFactory = GeoServerRestClient,
) -> ToolResponse:
    check_response = await check_instances(runtime_config, client_factory=client_factory)
    statuses = check_response.data.get("instances", [])
    summaries = [_to_summary(status) for status in statuses]
    metadata = dict(check_response.metadata)
    metadata.update({"tool": "list_catalog", "resource_types": ["instances"]})
    return ToolResponse(
        status=check_response.status,
        data={"instances": summaries},
        findings=check_response.findings,
        errors=check_response.errors,
        metadata=metadata,
    )


def _to_summary(status: InstanceConnectivityStatus) -> InstanceInventorySummary:
    unavailable_information: list[ToolError] = []
    if status.reason_code is not None:
        unavailable_information.append(
            ToolError(
                instance_id=status.instance_id,
                reason_code=status.reason_code,
                message=status.message or "Instance information unavailable",
                status_code=status.status_code,
                url=status.evidence_url,
            )
        )
    return InstanceInventorySummary(
        instance_id=status.instance_id,
        base_url=status.base_url,
        reachable=status.reachable,
        authenticated=status.authenticated,
        inspected_surfaces=[INSTANCE_SURFACE] if status.reachable and status.authenticated else [],
        unavailable_information=unavailable_information,
        server_version=status.server_version,
        reason_code=status.reason_code,
    )
