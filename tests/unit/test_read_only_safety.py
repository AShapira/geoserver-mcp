from __future__ import annotations

import inspect

import pytest
from pydantic import SecretStr

from geoserver_mcp.adapters.geoserver_rest import GeoServerRestClient, GeoServerRestResult
from geoserver_mcp.adapters.mcp import create_mcp_app
from geoserver_mcp.config import BasicCredentials, RuntimeConfig, RuntimeInstanceConfig
from geoserver_mcp.security.read_only import READ_ONLY_SAFETY_PROMPT, is_mutation_name


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
async def test_registered_mcp_tools_are_read_only_named() -> None:
    app = create_mcp_app(runtime_config=runtime_config(), client_factory=SuccessfulClient)

    tools = await app.list_tools()
    tool_names = {tool.name for tool in tools}

    assert "check_instances" in tool_names
    assert all(not is_mutation_name(name) for name in tool_names)


def test_geoserver_rest_client_public_methods_are_get_only() -> None:
    public_methods = {
        name
        for name, value in inspect.getmembers(GeoServerRestClient, predicate=inspect.isfunction)
        if not name.startswith("_")
    }
    source = inspect.getsource(GeoServerRestClient)

    assert {"get_connectivity_metadata", "get_json"} <= public_methods
    assert all(not is_mutation_name(name) for name in public_methods)
    assert all(name.startswith(("fetch_", "get_", "inspect_", "list_")) for name in public_methods)
    assert ".post(" not in source
    assert ".put(" not in source
    assert ".patch(" not in source
    assert ".delete(" not in source


@pytest.mark.anyio
async def test_read_only_safety_prompt_identifies_mutation_as_unsupported() -> None:
    app = create_mcp_app()

    prompts = await app.list_prompts()
    prompt_result = await app.get_prompt("read_only_safety")
    rendered = str(prompt_result).lower()

    assert "read_only_safety" in {prompt.name for prompt in prompts}
    assert "unsupported in v1" in READ_ONLY_SAFETY_PROMPT
    assert "create" in rendered
    assert "update" in rendered
    assert "delete" in rendered
    assert "reload" in rendered
    assert "purge" in rendered
    assert "unsupported in v1" in rendered
