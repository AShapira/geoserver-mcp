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

    async def list_workspaces(self) -> GeoServerRestResult:
        return GeoServerRestResult(
            status="success",
            data={
                "workspaces": {
                    "workspace": [
                        {
                            "name": "topp",
                            "href": f"{self._instance.base_url}/rest/workspaces/topp.json",
                        }
                    ]
                }
            },
            status_code=200,
            url=f"{self._instance.base_url}/rest/workspaces.json",
        )

    async def list_stores(self, workspace: str, store_type: str) -> GeoServerRestResult:
        if store_type == "data_stores":
            return GeoServerRestResult(
                status="success",
                data={"dataStores": {"dataStore": [{"name": "roads", "enabled": True}]}},
                status_code=200,
                url=f"{self._instance.base_url}/rest/workspaces/{workspace}/datastores.json",
            )
        if store_type == "coverage_stores":
            return GeoServerRestResult(
                status="success",
                data={"coverageStores": {"coverageStore": []}},
                status_code=200,
                url=f"{self._instance.base_url}/rest/workspaces/{workspace}/coveragestores.json",
            )
        return GeoServerRestResult(
            status="success",
            data={"wmsStores": {"wmsStore": []}},
            status_code=200,
            url=f"{self._instance.base_url}/rest/workspaces/{workspace}/wmsstores.json",
        )

    async def list_layers(self) -> GeoServerRestResult:
        return GeoServerRestResult(
            status="success",
            data={
                "layers": {
                    "layer": [
                        {
                            "name": "topp:states",
                            "type": "VECTOR",
                            "enabled": True,
                            "advertised": True,
                            "defaultStyle": {"name": "polygon"},
                            "resource": {"name": "states"},
                            "store": {"name": "roads"},
                        }
                    ]
                }
            },
            status_code=200,
            url=f"{self._instance.base_url}/rest/layers.json",
        )

    async def list_layer_groups(self) -> GeoServerRestResult:
        return GeoServerRestResult(
            status="success",
            data={"layerGroups": {"layerGroup": [{"name": "basemap"}]}},
            status_code=200,
            url=f"{self._instance.base_url}/rest/layergroups.json",
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
async def test_list_catalog_tool_returns_workspaces() -> None:
    app = create_mcp_app(runtime_config=runtime_config(), client_factory=SuccessfulClient)

    _, result = await app.call_tool("list_catalog", {"resource_types": ["workspaces"]})

    assert result["status"] == "success"
    assert result["data"]["workspaces"][0]["instance_id"] == "production"
    assert result["data"]["workspaces"][0]["name"] == "topp"
    assert result["data"]["workspaces"][0]["resource_id"] == "topp"
    assert result["metadata"]["resource_types"] == ["workspaces"]
    assert "prod-password" not in str(result)


@pytest.mark.anyio
async def test_list_catalog_tool_returns_stores() -> None:
    app = create_mcp_app(runtime_config=runtime_config(), client_factory=SuccessfulClient)

    _, result = await app.call_tool("list_catalog", {"resource_types": ["stores"]})

    assert result["status"] == "success"
    assert result["data"]["stores"][0]["instance_id"] == "production"
    assert result["data"]["stores"][0]["workspace"] == "topp"
    assert result["data"]["stores"][0]["name"] == "roads"
    assert result["data"]["stores"][0]["store_type"] == "data_stores"
    assert result["data"]["stores"][0]["enabled"] is True
    assert result["metadata"]["resource_types"] == ["stores"]
    assert "prod-password" not in str(result)


@pytest.mark.anyio
async def test_list_catalog_tool_returns_layers_and_layer_groups() -> None:
    app = create_mcp_app(runtime_config=runtime_config(), client_factory=SuccessfulClient)

    _, result = await app.call_tool("list_catalog", {"resource_types": ["layers"]})

    assert result["status"] == "success"
    assert result["data"]["layers"][0]["instance_id"] == "production"
    assert result["data"]["layers"][0]["name"] == "topp:states"
    assert result["data"]["layers"][0]["workspace"] == "topp"
    assert result["data"]["layers"][0]["resource_type"] == "VECTOR"
    assert result["data"]["layers"][0]["default_style"] == "polygon"
    assert result["data"]["layer_groups"][0]["name"] == "basemap"
    assert result["metadata"]["resource_types"] == ["layers"]
    assert "prod-password" not in str(result)


@pytest.mark.anyio
async def test_list_catalog_rejects_unsupported_resource_types() -> None:
    app = create_mcp_app(runtime_config=runtime_config(), client_factory=SuccessfulClient)

    _, result = await app.call_tool("list_catalog", {"resource_types": ["styles"]})

    assert result["status"] == "failed"
    assert result["errors"][0]["reason_code"] == "unsupported_endpoint"
    assert result["metadata"]["resource_types"] == ["styles"]


@pytest.mark.anyio
async def test_list_catalog_rejects_mixed_resource_types_until_cache_story() -> None:
    app = create_mcp_app(runtime_config=runtime_config(), client_factory=SuccessfulClient)

    _, result = await app.call_tool(
        "list_catalog",
        {"resource_types": ["instances", "workspaces"]},
    )

    assert result["status"] == "failed"
    assert result["errors"][0]["reason_code"] == "unsupported_endpoint"
    assert result["metadata"]["resource_types"] == ["instances", "workspaces"]
