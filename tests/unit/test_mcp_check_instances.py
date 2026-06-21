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
async def test_check_instances_tool_is_absent_without_runtime_config() -> None:
    app = create_mcp_app()

    tools = await app.list_tools()

    assert "check_instances" not in {tool.name for tool in tools}


@pytest.mark.anyio
async def test_check_instances_tool_is_registered_and_callable_with_runtime_config() -> None:
    app = create_mcp_app(
        runtime_config=runtime_config(),
        client_factory=SuccessfulClient,
    )

    tools = await app.list_tools()
    _, result = await app.call_tool("check_instances", {})

    assert "check_instances" in {tool.name for tool in tools}
    assert result["status"] == "success"
    assert result["data"]["instances"][0]["instance_id"] == "production"
    assert result["data"]["instances"][0]["server_version"] == "2.26.0"
    assert "prod-password" not in str(result)


def test_create_mcp_app_accepts_callable_client_factory_type() -> None:
    app = create_mcp_app(
        runtime_config=runtime_config(),
        client_factory=SuccessfulClient,
    )

    assert callable(app.call_tool)
