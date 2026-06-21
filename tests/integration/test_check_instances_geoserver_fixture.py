from __future__ import annotations

import os

import anyio
import pytest
from pydantic import SecretStr

from geoserver_mcp.config import BasicCredentials, RuntimeConfig, RuntimeInstanceConfig
from geoserver_mcp.domain import ResponseStatus
from geoserver_mcp.services import check_instances


def fixture_runtime_config() -> RuntimeConfig:
    return RuntimeConfig(
        instances=(
            RuntimeInstanceConfig(
                id="local-fixture",
                base_url=os.getenv("GEOSERVER_FIXTURE_URL", "http://localhost:8080/geoserver"),
                data_directory=None,
                credentials=BasicCredentials(
                    username=SecretStr(os.getenv("GEOSERVER_FIXTURE_USER", "admin")),
                    password=SecretStr(os.getenv("GEOSERVER_FIXTURE_PASSWORD", "geoserver")),
                ),
            ),
        )
    )


@pytest.mark.anyio
async def test_check_instances_against_docker_compose_geoserver_fixture() -> None:
    if os.getenv("GEOSERVER_MCP_RUN_FIXTURE_TESTS") != "1":
        pytest.skip("set GEOSERVER_MCP_RUN_FIXTURE_TESTS=1 to run GeoServer fixture tests")

    response = None
    for _ in range(20):
        response = await check_instances(fixture_runtime_config())
        if response.status == ResponseStatus.SUCCESS:
            break
        await anyio.sleep(3)

    assert response is not None
    assert response.status == ResponseStatus.SUCCESS
    instances = response.data["instances"]
    assert len(instances) == 1
    assert instances[0].instance_id == "local-fixture"
    assert instances[0].reachable is True
    assert instances[0].authenticated is True
