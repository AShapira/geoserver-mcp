from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from typing import Any, Protocol

from geoserver_mcp.adapters.geoserver_rest import GeoServerRestClient, GeoServerRestResult
from geoserver_mcp.config import RuntimeConfig, RuntimeInstanceConfig
from geoserver_mcp.domain import (
    InstanceConnectivityStatus,
    ReasonCode,
    ResponseStatus,
    ToolError,
    ToolResponse,
)
from geoserver_mcp.security import redact_text, redact_value


class ConnectivityClient(Protocol):
    async def get_connectivity_metadata(self) -> GeoServerRestResult: ...


ClientFactory = Callable[[RuntimeInstanceConfig], ConnectivityClient]


async def check_instances(
    runtime_config: RuntimeConfig,
    *,
    client_factory: ClientFactory = GeoServerRestClient,
) -> ToolResponse:
    known_secrets = _known_secret_values(runtime_config)
    statuses: list[InstanceConnectivityStatus] = []
    errors: list[ToolError] = []

    for instance in runtime_config.instances:
        try:
            result = await client_factory(instance).get_connectivity_metadata()
        except Exception:
            result = GeoServerRestResult(
                status="failed",
                reason_code=ReasonCode.UNKNOWN,
                message="unexpected GeoServer instance check failure",
            )
        if result.succeeded:
            statuses.append(_success_status(instance, result, known_secrets))
            continue

        failed_status = _failure_status(instance, result, known_secrets)
        statuses.append(failed_status)
        errors.append(
            ToolError(
                instance_id=instance.id,
                reason_code=failed_status.reason_code or ReasonCode.UNKNOWN,
                message=failed_status.message or "GeoServer instance check failed",
                status_code=failed_status.status_code,
                url=failed_status.evidence_url,
            )
        )

    return ToolResponse(
        status=_overall_status(statuses),
        data={"instances": statuses},
        errors=errors,
        metadata={
            "tool": "check_instances",
            "generated_at": datetime.now(UTC).isoformat(),
            "instances": [instance.id for instance in runtime_config.instances],
        },
    )


def _success_status(
    instance: RuntimeInstanceConfig,
    result: GeoServerRestResult,
    known_secrets: Sequence[str],
) -> InstanceConnectivityStatus:
    data = redact_value(result.data or {}, known_secrets)
    version = _extract_version(data)
    return InstanceConnectivityStatus(
        instance_id=instance.id,
        base_url=_redact(instance.base_url, known_secrets),
        reachable=True,
        authenticated=True,
        server_version=_redact(version, known_secrets) if version else None,
        status_code=result.status_code,
        evidence_url=_redact(result.url, known_secrets) if result.url else None,
    )


def _failure_status(
    instance: RuntimeInstanceConfig,
    result: GeoServerRestResult,
    known_secrets: Sequence[str],
) -> InstanceConnectivityStatus:
    reason_code = result.reason_code or ReasonCode.UNKNOWN
    reachable = reason_code not in {ReasonCode.NETWORK_ERROR, ReasonCode.UNKNOWN} or (
        result.status_code is not None
    )
    return InstanceConnectivityStatus(
        instance_id=instance.id,
        base_url=_redact(instance.base_url, known_secrets),
        reachable=reachable,
        authenticated=False,
        reason_code=reason_code,
        message=_redact(result.message or "GeoServer instance check failed", known_secrets),
        status_code=result.status_code,
        evidence_url=_redact(result.url, known_secrets) if result.url else None,
    )


def _overall_status(statuses: Sequence[InstanceConnectivityStatus]) -> ResponseStatus:
    successful_count = sum(1 for item in statuses if item.reachable and item.authenticated)
    if successful_count == len(statuses):
        return ResponseStatus.SUCCESS
    if successful_count == 0:
        return ResponseStatus.FAILED
    return ResponseStatus.PARTIAL


def _extract_version(value: Any) -> str | None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key).lower() == "version" and isinstance(item, str):
                return item
            found = _extract_version(item)
            if found:
                return found
    if isinstance(value, list | tuple):
        for item in value:
            found = _extract_version(item)
            if found:
                return found
    return None


def _known_secret_values(runtime_config: RuntimeConfig) -> tuple[str, ...]:
    secrets: list[str] = []
    for instance in runtime_config.instances:
        secrets.extend(instance.credentials.as_basic_auth_tuple())
    return tuple(secrets)


def _redact(value: str, known_secrets: Sequence[str]) -> str:
    return redact_text(value, known_secrets)
