from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from geoserver_mcp.domain.enums import ReasonCode
from geoserver_mcp.domain.responses import ToolError


class InstanceInventorySummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    instance_id: str
    base_url: str
    reachable: bool
    authenticated: bool
    inspected_surfaces: list[str] = Field(default_factory=list)
    unavailable_information: list[ToolError] = Field(default_factory=list)
    server_version: str | None = None
    reason_code: ReasonCode | None = None


class WorkspaceInventoryItem(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    instance_id: str
    name: str
    resource_id: str
    href: str | None = None


class StoreInventoryItem(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    instance_id: str
    workspace: str
    name: str
    resource_id: str
    store_type: str
    enabled: bool | None = None
    href: str | None = None


class LayerInventoryItem(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    instance_id: str
    name: str
    resource_id: str
    workspace: str | None = None
    resource_type: str | None = None
    enabled: bool | None = None
    advertised: bool | None = None
    default_style: str | None = None
    store: str | None = None
    resource: str | None = None
    href: str | None = None


class LayerGroupInventoryItem(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    instance_id: str
    name: str
    resource_id: str
    workspace: str | None = None
    layers: list[str] = Field(default_factory=list)
    href: str | None = None
