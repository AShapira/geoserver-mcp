from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from geoserver_mcp.domain.enums import ReasonCode, ResponseStatus


class ToolError(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    reason_code: ReasonCode
    message: str
    instance_id: str | None = None
    status_code: int | None = None
    url: str | None = None


class InstanceConnectivityStatus(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    instance_id: str
    base_url: str
    reachable: bool
    authenticated: bool
    server_version: str | None = None
    reason_code: ReasonCode | None = None
    message: str | None = None
    status_code: int | None = None
    evidence_url: str | None = None


class ToolResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    status: ResponseStatus
    data: dict[str, Any] = Field(default_factory=dict)
    findings: list[Any] = Field(default_factory=list)
    errors: list[ToolError] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
