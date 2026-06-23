from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from typing import Any, Protocol

from geoserver_mcp.adapters.geoserver_rest import GeoServerRestClient, GeoServerRestResult
from geoserver_mcp.config import RuntimeConfig
from geoserver_mcp.domain import (
    InstanceConnectivityStatus,
    InstanceInventorySummary,
    LayerGroupInventoryItem,
    LayerInventoryItem,
    ReasonCode,
    ResponseStatus,
    StoreInventoryItem,
    ToolError,
    ToolResponse,
    WorkspaceInventoryItem,
)
from geoserver_mcp.security import redact_text, redact_url
from geoserver_mcp.services.instance_service import ClientFactory, check_instances

INSTANCE_SURFACE = "geoserver_rest:about_version"
WORKSPACE_SURFACE = "geoserver_rest:workspaces"
STORE_SURFACES = {
    "data_stores": "geoserver_rest:datastores",
    "coverage_stores": "geoserver_rest:coveragestores",
    "wms_stores": "geoserver_rest:wmsstores",
}
LAYER_SURFACES = {
    "layers": "geoserver_rest:layers",
    "layer_groups": "geoserver_rest:layergroups",
}
STORE_RESPONSE_KEYS = {
    "data_stores": ("dataStores", "dataStore"),
    "coverage_stores": ("coverageStores", "coverageStore"),
    "wms_stores": ("wmsStores", "wmsStore"),
}


class WorkspaceClient(Protocol):
    async def list_workspaces(self) -> GeoServerRestResult: ...


class StoreClient(WorkspaceClient, Protocol):
    async def list_stores(self, workspace: str, store_type: str) -> GeoServerRestResult: ...


class LayerClient(Protocol):
    async def list_layers(self) -> GeoServerRestResult: ...

    async def list_layer_groups(self) -> GeoServerRestResult: ...


WorkspaceClientFactory = Callable[..., WorkspaceClient]
StoreClientFactory = Callable[..., StoreClient]
LayerClientFactory = Callable[..., LayerClient]


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


async def list_workspace_inventory(
    runtime_config: RuntimeConfig,
    *,
    client_factory: WorkspaceClientFactory = GeoServerRestClient,
) -> ToolResponse:
    known_secrets = _known_secret_values(runtime_config)
    workspaces: list[WorkspaceInventoryItem] = []
    errors: list[ToolError] = []
    successful_count = 0

    for instance in runtime_config.instances:
        try:
            result = await client_factory(instance).list_workspaces()
        except Exception:
            result = GeoServerRestResult(
                status="failed",
                reason_code=ReasonCode.UNKNOWN,
                message="unexpected GeoServer workspace inventory failure",
            )
        if result.succeeded:
            extracted, parse_error = _extract_workspace_items(instance.id, result, known_secrets)
            if parse_error is None:
                successful_count += 1
                workspaces.extend(extracted)
                continue
            result = parse_error

        errors.append(
            ToolError(
                instance_id=instance.id,
                reason_code=result.reason_code or ReasonCode.UNKNOWN,
                message=_redact(
                    result.message or "GeoServer workspace inventory failed",
                    known_secrets,
                ),
                status_code=result.status_code,
                url=_redact(result.url, known_secrets) if result.url else None,
            )
        )

    return ToolResponse(
        status=_catalog_status(successful_count, len(runtime_config.instances)),
        data={"workspaces": workspaces},
        errors=errors,
        metadata={
            "tool": "list_catalog",
            "resource_types": ["workspaces"],
            "inspected_surfaces": [WORKSPACE_SURFACE],
            "generated_at": datetime.now(UTC).isoformat(),
            "instances": [instance.id for instance in runtime_config.instances],
        },
    )


async def list_store_inventory(
    runtime_config: RuntimeConfig,
    *,
    client_factory: StoreClientFactory = GeoServerRestClient,
) -> ToolResponse:
    known_secrets = _known_secret_values(runtime_config)
    stores: list[StoreInventoryItem] = []
    errors: list[ToolError] = []
    successful_operations = 0
    failed_operations = 0

    for instance in runtime_config.instances:
        try:
            client = client_factory(instance)
            workspace_result = await client.list_workspaces()
        except Exception:
            workspace_result = GeoServerRestResult(
                status="failed",
                reason_code=ReasonCode.UNKNOWN,
                message="unexpected GeoServer workspace inventory failure",
            )
            client = None

        if not workspace_result.succeeded:
            failed_operations += 1
            errors.append(_tool_error(instance.id, workspace_result, known_secrets))
            continue

        workspace_items, parse_error = _extract_workspace_items(
            instance.id,
            workspace_result,
            known_secrets,
        )
        if parse_error is not None or client is None:
            failed_operations += 1
            errors.append(_tool_error(instance.id, parse_error or workspace_result, known_secrets))
            continue

        for workspace in workspace_items:
            for store_type in STORE_RESPONSE_KEYS:
                try:
                    store_result = await client.list_stores(workspace.name, store_type)
                except Exception:
                    store_result = GeoServerRestResult(
                        status="failed",
                        reason_code=ReasonCode.UNKNOWN,
                        message="unexpected GeoServer store inventory failure",
                    )
                if store_result.succeeded:
                    extracted, store_parse_error = _extract_store_items(
                        instance.id,
                        workspace.name,
                        store_type,
                        store_result,
                        known_secrets,
                    )
                    if store_parse_error is None:
                        successful_operations += 1
                        stores.extend(extracted)
                        continue
                    store_result = store_parse_error

                failed_operations += 1
                errors.append(_tool_error(instance.id, store_result, known_secrets))

    return ToolResponse(
        status=_operation_status(successful_operations, failed_operations),
        data={"stores": stores},
        errors=errors,
        metadata={
            "tool": "list_catalog",
            "resource_types": ["stores"],
            "inspected_surfaces": list(STORE_SURFACES.values()),
            "generated_at": datetime.now(UTC).isoformat(),
            "instances": [instance.id for instance in runtime_config.instances],
        },
    )


async def list_layer_inventory(
    runtime_config: RuntimeConfig,
    *,
    client_factory: LayerClientFactory = GeoServerRestClient,
) -> ToolResponse:
    known_secrets = _known_secret_values(runtime_config)
    layers: list[LayerInventoryItem] = []
    layer_groups: list[LayerGroupInventoryItem] = []
    findings: list[dict[str, object]] = []
    errors: list[ToolError] = []
    successful_operations = 0
    failed_operations = 0

    for instance in runtime_config.instances:
        try:
            client = client_factory(instance)
        except Exception:
            result = GeoServerRestResult(
                status="failed",
                reason_code=ReasonCode.UNKNOWN,
                message="unexpected GeoServer layer inventory client failure",
            )
            failed_operations += 2
            errors.append(_tool_error(instance.id, result, known_secrets))
            continue

        try:
            layer_result = await client.list_layers()
        except Exception:
            layer_result = GeoServerRestResult(
                status="failed",
                reason_code=ReasonCode.UNKNOWN,
                message="unexpected GeoServer layer inventory failure",
            )
        if layer_result.succeeded:
            extracted, extracted_findings, parse_error = _extract_layer_items(
                instance.id,
                layer_result,
                known_secrets,
            )
            if parse_error is None:
                successful_operations += 1
                layers.extend(extracted)
                findings.extend(extracted_findings)
            else:
                failed_operations += 1
                errors.append(_tool_error(instance.id, parse_error, known_secrets))
        else:
            failed_operations += 1
            errors.append(_tool_error(instance.id, layer_result, known_secrets))

        try:
            group_result = await client.list_layer_groups()
        except Exception:
            group_result = GeoServerRestResult(
                status="failed",
                reason_code=ReasonCode.UNKNOWN,
                message="unexpected GeoServer layer-group inventory failure",
            )
        if group_result.succeeded:
            extracted_groups, group_findings, group_parse_error = _extract_layer_group_items(
                instance.id,
                group_result,
                known_secrets,
            )
            if group_parse_error is None:
                successful_operations += 1
                layer_groups.extend(extracted_groups)
                findings.extend(group_findings)
            else:
                failed_operations += 1
                errors.append(_tool_error(instance.id, group_parse_error, known_secrets))
        else:
            failed_operations += 1
            errors.append(_tool_error(instance.id, group_result, known_secrets))

    return ToolResponse(
        status=_operation_status(successful_operations, failed_operations),
        data={"layers": layers, "layer_groups": layer_groups},
        findings=findings,
        errors=errors,
        metadata={
            "tool": "list_catalog",
            "resource_types": ["layers"],
            "inspected_surfaces": list(LAYER_SURFACES.values()),
            "generated_at": datetime.now(UTC).isoformat(),
            "instances": [instance.id for instance in runtime_config.instances],
        },
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


def _extract_workspace_items(
    instance_id: str,
    result: GeoServerRestResult,
    known_secrets: Sequence[str],
) -> tuple[list[WorkspaceInventoryItem], GeoServerRestResult | None]:
    data = result.data
    workspace_entries = _workspace_entries(data)
    if workspace_entries is None:
        return [], GeoServerRestResult(
            status="failed",
            reason_code=ReasonCode.PARSE_ERROR,
            message="GeoServer workspace response did not match the expected shape",
            status_code=result.status_code,
            url=result.url,
        )

    items: list[WorkspaceInventoryItem] = []
    for entry in workspace_entries:
        item = _workspace_item(instance_id, entry, known_secrets)
        if item is not None:
            items.append(item)
    return items, None


def _workspace_entries(data: Mapping[str, Any] | None) -> list[Mapping[str, Any] | str] | None:
    if not isinstance(data, Mapping):
        return None
    workspaces = data.get("workspaces")
    if not isinstance(workspaces, Mapping):
        return None
    workspace = workspaces.get("workspace", [])
    if workspace is None:
        return []
    if isinstance(workspace, list):
        return workspace
    if isinstance(workspace, Mapping | str):
        return [workspace]
    return None


def _workspace_item(
    instance_id: str,
    entry: Mapping[str, Any] | str,
    known_secrets: Sequence[str],
) -> WorkspaceInventoryItem | None:
    if isinstance(entry, str):
        name = entry
        href = None
    else:
        raw_name = entry.get("name")
        if not isinstance(raw_name, str) or not raw_name:
            return None
        name = raw_name
        raw_href = entry.get("href")
        href = raw_href if isinstance(raw_href, str) and raw_href else None

    safe_name = _redact(name, known_secrets)
    return WorkspaceInventoryItem(
        instance_id=instance_id,
        name=safe_name,
        resource_id=safe_name,
        href=_redact(href, known_secrets) if href else None,
    )


def _extract_store_items(
    instance_id: str,
    workspace: str,
    store_type: str,
    result: GeoServerRestResult,
    known_secrets: Sequence[str],
) -> tuple[list[StoreInventoryItem], GeoServerRestResult | None]:
    store_entries = _store_entries(result.data, store_type)
    if store_entries is None:
        return [], GeoServerRestResult(
            status="failed",
            reason_code=ReasonCode.PARSE_ERROR,
            message="GeoServer store response did not match the expected shape",
            status_code=result.status_code,
            url=result.url,
        )

    items: list[StoreInventoryItem] = []
    for entry in store_entries:
        item = _store_item(instance_id, workspace, store_type, entry, known_secrets)
        if item is not None:
            items.append(item)
    return items, None


def _store_entries(
    data: Mapping[str, Any] | None,
    store_type: str,
) -> list[Mapping[str, Any] | str] | None:
    if not isinstance(data, Mapping):
        return None
    container_key, item_key = STORE_RESPONSE_KEYS[store_type]
    container = data.get(container_key)
    if not isinstance(container, Mapping):
        return None
    store = container.get(item_key, [])
    if store is None:
        return []
    if isinstance(store, list):
        return store
    if isinstance(store, Mapping | str):
        return [store]
    return None


def _store_item(
    instance_id: str,
    workspace: str,
    store_type: str,
    entry: Mapping[str, Any] | str,
    known_secrets: Sequence[str],
) -> StoreInventoryItem | None:
    if isinstance(entry, str):
        name = entry
        href = None
        enabled = None
    else:
        raw_name = entry.get("name")
        if not isinstance(raw_name, str) or not raw_name:
            return None
        name = raw_name
        raw_href = entry.get("href")
        href = raw_href if isinstance(raw_href, str) and raw_href else None
        raw_enabled = entry.get("enabled")
        enabled = raw_enabled if isinstance(raw_enabled, bool) else None

    safe_workspace = _redact(workspace, known_secrets)
    safe_name = _redact(name, known_secrets)
    return StoreInventoryItem(
        instance_id=instance_id,
        workspace=safe_workspace,
        name=safe_name,
        resource_id=f"{safe_workspace}:{safe_name}",
        store_type=store_type,
        enabled=enabled,
        href=_redact(href, known_secrets) if href else None,
    )


def _extract_layer_items(
    instance_id: str,
    result: GeoServerRestResult,
    known_secrets: Sequence[str],
) -> tuple[list[LayerInventoryItem], list[dict[str, object]], GeoServerRestResult | None]:
    layer_entries = _layer_entries(result.data)
    if layer_entries is None:
        return (
            [],
            [],
            GeoServerRestResult(
                status="failed",
                reason_code=ReasonCode.PARSE_ERROR,
                message="GeoServer layer response did not match the expected shape",
                status_code=result.status_code,
                url=result.url,
            ),
        )

    items: list[LayerInventoryItem] = []
    findings: list[dict[str, object]] = []
    for index, entry in enumerate(layer_entries):
        item, item_findings = _layer_item(instance_id, entry, known_secrets)
        if item is not None:
            items.append(item)
            findings.extend(item_findings)
        else:
            findings.append(
                _catalog_finding(
                    instance_id,
                    "layer",
                    f"entry[{index}]",
                    (
                        "Layer entry was skipped because required name metadata was "
                        "unavailable or malformed."
                    ),
                )
            )
    return items, findings, None


def _layer_entries(data: Mapping[str, Any] | None) -> list[Mapping[str, Any] | str] | None:
    if not isinstance(data, Mapping):
        return None
    layers = data.get("layers")
    if not isinstance(layers, Mapping):
        return None
    layer = layers.get("layer", [])
    if layer is None:
        return []
    if isinstance(layer, list):
        return layer
    if isinstance(layer, Mapping | str):
        return [layer]
    return None


def _layer_item(
    instance_id: str,
    entry: Mapping[str, Any] | str,
    known_secrets: Sequence[str],
) -> tuple[LayerInventoryItem | None, list[dict[str, object]]]:
    if isinstance(entry, str):
        safe_name = _redact(entry, known_secrets)
        workspace = _workspace_from_name(safe_name)
        return (
            LayerInventoryItem(
                instance_id=instance_id,
                name=safe_name,
                resource_id=_resource_id(safe_name, workspace),
                workspace=workspace,
            ),
            [],
        )

    raw_name = entry.get("name")
    if not isinstance(raw_name, str) or not raw_name:
        return None, []
    safe_name = _redact(raw_name, known_secrets)
    workspace = _workspace_from_entry(entry, safe_name, known_secrets)
    resource = _named_reference(entry.get("resource"), known_secrets)
    store = _named_reference(entry.get("store"), known_secrets)
    findings: list[dict[str, object]] = []
    if "resource" in entry and resource is None:
        findings.append(
            _related_resource_finding(
                instance_id,
                safe_name,
                "Layer related resource metadata was unavailable or malformed.",
            )
        )
    if "store" in entry and store is None:
        findings.append(
            _related_resource_finding(
                instance_id,
                safe_name,
                "Layer related store metadata was unavailable or malformed.",
            )
        )

    raw_href = entry.get("href")
    href = raw_href if isinstance(raw_href, str) and raw_href else None
    return (
        LayerInventoryItem(
            instance_id=instance_id,
            name=safe_name,
            resource_id=_resource_id(safe_name, workspace),
            workspace=workspace,
            resource_type=_resource_type(entry),
            enabled=_optional_bool(entry.get("enabled")),
            advertised=_optional_bool(entry.get("advertised")),
            default_style=_default_style(entry, known_secrets),
            store=store,
            resource=resource,
            href=_redact_url(href, known_secrets) if href else None,
        ),
        findings,
    )


def _extract_layer_group_items(
    instance_id: str,
    result: GeoServerRestResult,
    known_secrets: Sequence[str],
) -> tuple[list[LayerGroupInventoryItem], list[dict[str, object]], GeoServerRestResult | None]:
    group_entries = _layer_group_entries(result.data)
    if group_entries is None:
        return (
            [],
            [],
            GeoServerRestResult(
                status="failed",
                reason_code=ReasonCode.PARSE_ERROR,
                message="GeoServer layer-group response did not match the expected shape",
                status_code=result.status_code,
                url=result.url,
            ),
        )

    items: list[LayerGroupInventoryItem] = []
    findings: list[dict[str, object]] = []
    for index, entry in enumerate(group_entries):
        item, item_findings = _layer_group_item(instance_id, entry, known_secrets)
        if item is not None:
            items.append(item)
            findings.extend(item_findings)
        else:
            findings.append(
                _catalog_finding(
                    instance_id,
                    "layer_group",
                    f"entry[{index}]",
                    (
                        "Layer-group entry was skipped because required name metadata was "
                        "unavailable or malformed."
                    ),
                )
            )
    return items, findings, None


def _layer_group_entries(data: Mapping[str, Any] | None) -> list[Mapping[str, Any] | str] | None:
    if not isinstance(data, Mapping):
        return None
    groups = data.get("layerGroups")
    if not isinstance(groups, Mapping):
        return None
    group = groups.get("layerGroup", [])
    if group is None:
        return []
    if isinstance(group, list):
        return group
    if isinstance(group, Mapping | str):
        return [group]
    return None


def _layer_group_item(
    instance_id: str,
    entry: Mapping[str, Any] | str,
    known_secrets: Sequence[str],
) -> tuple[LayerGroupInventoryItem | None, list[dict[str, object]]]:
    if isinstance(entry, str):
        safe_name = _redact(entry, known_secrets)
        workspace = _workspace_from_name(safe_name)
        return (
            LayerGroupInventoryItem(
                instance_id=instance_id,
                name=safe_name,
                resource_id=_resource_id(safe_name, workspace),
                workspace=workspace,
            ),
            [],
        )

    raw_name = entry.get("name")
    if not isinstance(raw_name, str) or not raw_name:
        return None, []
    safe_name = _redact(raw_name, known_secrets)
    raw_href = entry.get("href")
    href = raw_href if isinstance(raw_href, str) and raw_href else None
    workspace = _workspace_from_entry(entry, safe_name, known_secrets) or (
        _workspace_from_href(href) if href else None
    )
    layers, malformed_membership = _published_layer_names(entry, known_secrets)
    findings: list[dict[str, object]] = []
    if malformed_membership:
        findings.append(
            _catalog_finding(
                instance_id,
                "layer_group",
                _resource_id(safe_name, workspace),
                "Layer-group membership metadata was unavailable or malformed.",
            )
        )
    return (
        LayerGroupInventoryItem(
            instance_id=instance_id,
            name=safe_name,
            resource_id=_resource_id(safe_name, workspace),
            workspace=workspace,
            layers=layers,
            href=_redact_url(href, known_secrets) if href else None,
        ),
        findings,
    )


def _workspace_from_entry(
    entry: Mapping[str, Any],
    safe_name: str,
    known_secrets: Sequence[str],
) -> str | None:
    workspace = _named_reference(entry.get("workspace"), known_secrets)
    return workspace or _workspace_from_name(safe_name)


def _workspace_from_name(name: str) -> str | None:
    if ":" not in name:
        return None
    workspace, _ = name.split(":", 1)
    return workspace or None


def _workspace_from_href(href: str) -> str | None:
    parts = href.split("/")
    for index, part in enumerate(parts):
        if part == "workspaces" and index + 1 < len(parts):
            workspace = parts[index + 1]
            if workspace:
                return workspace.removesuffix(".json")
    return None


def _resource_id(name: str, workspace: str | None) -> str:
    if ":" in name or workspace is None:
        return name
    return f"{workspace}:{name}"


def _resource_type(entry: Mapping[str, Any]) -> str | None:
    raw_type = entry.get("type") or entry.get("resource_type")
    if isinstance(raw_type, str) and raw_type:
        return raw_type
    raw_resource = entry.get("resource")
    if isinstance(raw_resource, Mapping):
        raw_class = raw_resource.get("@class")
        if isinstance(raw_class, str) and raw_class:
            return raw_class.rsplit(".", maxsplit=1)[-1]
    return None


def _default_style(entry: Mapping[str, Any], known_secrets: Sequence[str]) -> str | None:
    return _named_reference(
        entry.get("defaultStyle") or entry.get("default_style"),
        known_secrets,
    )


def _published_layer_names(
    entry: Mapping[str, Any],
    known_secrets: Sequence[str],
) -> tuple[list[str], bool]:
    candidates = (entry.get("layers"), entry.get("publishables"))
    for candidate in candidates:
        if candidate is None:
            continue
        entries = _reference_entries(candidate)
        if entries is not None:
            return [
                layer
                for raw_entry in entries
                if (layer := _named_reference(raw_entry, known_secrets)) is not None
            ], False
        return [], True
    return [], False


def _reference_entries(value: object) -> list[Mapping[str, Any] | str] | None:
    if value is None:
        return None
    if isinstance(value, list):
        return value
    if isinstance(value, Mapping):
        for key in ("layer", "published", "publishable"):
            entry = value.get(key)
            if entry is None:
                continue
            if isinstance(entry, list):
                return entry
            if isinstance(entry, Mapping | str):
                return [entry]
        return None
    if isinstance(value, str):
        return [value]
    return None


def _named_reference(value: object, known_secrets: Sequence[str]) -> str | None:
    if isinstance(value, str) and value:
        return _redact(value, known_secrets)
    if isinstance(value, Mapping):
        raw_name = value.get("name")
        if isinstance(raw_name, str) and raw_name:
            return _redact(raw_name, known_secrets)
    return None


def _optional_bool(value: object) -> bool | None:
    return value if isinstance(value, bool) else None


def _related_resource_finding(
    instance_id: str,
    layer_name: str,
    message: str,
) -> dict[str, object]:
    return {
        "severity": "warning",
        "reason_code": ReasonCode.PARTIAL_RESULT.value,
        "instance_id": instance_id,
        "resource": {"type": "layer", "name": layer_name},
        "message": message,
        "suggested_next_step": "Inspect catalog resource detail when that story is available.",
    }


def _catalog_finding(
    instance_id: str,
    resource_type: str,
    resource_name: str,
    message: str,
) -> dict[str, object]:
    return {
        "severity": "warning",
        "reason_code": ReasonCode.PARTIAL_RESULT.value,
        "instance_id": instance_id,
        "resource": {"type": resource_type, "name": resource_name},
        "message": message,
        "suggested_next_step": "Inspect catalog resource detail when that story is available.",
    }


def _catalog_status(successful_count: int, total_count: int) -> ResponseStatus:
    if successful_count == total_count:
        return ResponseStatus.SUCCESS
    if successful_count == 0:
        return ResponseStatus.FAILED
    return ResponseStatus.PARTIAL


def _operation_status(successful_count: int, failed_count: int) -> ResponseStatus:
    if failed_count == 0:
        return ResponseStatus.SUCCESS
    if successful_count == 0:
        return ResponseStatus.FAILED
    return ResponseStatus.PARTIAL


def _tool_error(
    instance_id: str,
    result: GeoServerRestResult,
    known_secrets: Sequence[str],
) -> ToolError:
    return ToolError(
        instance_id=instance_id,
        reason_code=result.reason_code or ReasonCode.UNKNOWN,
        message=_redact(result.message or "GeoServer catalog inventory failed", known_secrets),
        status_code=result.status_code,
        url=_redact(result.url, known_secrets) if result.url else None,
    )


def _known_secret_values(runtime_config: RuntimeConfig) -> tuple[str, ...]:
    secrets: list[str] = []
    for instance in runtime_config.instances:
        secrets.extend(instance.credentials.as_basic_auth_tuple())
    return tuple(secrets)


def _redact(value: str, known_secrets: Sequence[str]) -> str:
    return redact_text(value, known_secrets)


def _redact_url(value: str, known_secrets: Sequence[str]) -> str:
    return redact_url(value, known_secrets)
