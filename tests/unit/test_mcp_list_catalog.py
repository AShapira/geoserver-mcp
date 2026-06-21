from __future__ import annotations

import pytest
from pydantic import SecretStr

from geoserver_mcp.adapters.geoserver_rest import GeoServerRestResult
from geoserver_mcp.adapters.mcp import create_mcp_app
from geoserver_mcp.config import BasicCredentials, RuntimeConfig, RuntimeInstanceConfig


def runtime_config() -> RuntimeConfig:
    return RuntimeConfig(
        instances=(
            RuntimeInstanceConfig(
                id="production",
                base_url="https://prod.example.com/geoserver",
                data_directory=None,
                credentials=BasicCredentials(
                    username=SecretStr("prod-user"),
                    password=SecretStr("prod-password"),
                ),
            ),
        )
    )


class SuccessfulClient:
    def __init__(self, instance: RuntimeInstanceConfig) -> None:
        self._instance = instance

    async def get_connectivity_metadata(self) -> GeoServerRestResult:
        return GeoServerRestResult(
            status="success",
            data={"about": {"resource": [{"Version": "2.26.0"}]}},
            status_code=200,
            url=f"{self._instance.base_url}/rest/about/version.json",
        )


@pytest.mark.anyio
async def test_list_catalog_tool_returns_instance_summaries() -> None:
    app = create_mcp_app(runtime_config=runtime_config(), client_factory=SuccessfulClient)

    tools = await app.list_tools()
    _, result = await app.call_tool("list_catalog", {"resource_types": ["instances"]})

    assert "list_catalog" in {tool.name for tool in tools}
    assert result["status"] == "success"
    assert result["data"]["instances"][0]["instance_id"] == "production"
    assert result["data"]["instances"][0]["inspected_surfaces"] == ["geoserver_rest:about_version"]
    assert "prod-password" not in str(result)


@pytest.mark.anyio
async def test_list_catalog_defaults_to_instance_summaries() -> None:
    app = create_mcp_app(runtime_config=runtime_config(), client_factory=SuccessfulClient)

    _, result = await app.call_tool("list_catalog", {})

    assert result["status"] == "success"
    assert result["metadata"]["resource_types"] == ["instances"]


@pytest.mark.anyio
async def test_list_catalog_rejects_unsupported_resource_types() -> None:
    app = create_mcp_app(runtime_config=runtime_config(), client_factory=SuccessfulClient)

    _, result = await app.call_tool("list_catalog", {"resource_types": ["workspaces"]})

    assert result["status"] == "failed"
    assert result["errors"][0]["reason_code"] == "unsupported_endpoint"
    assert result["metadata"]["resource_types"] == ["workspaces"]
