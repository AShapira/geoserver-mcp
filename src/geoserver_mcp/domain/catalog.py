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
