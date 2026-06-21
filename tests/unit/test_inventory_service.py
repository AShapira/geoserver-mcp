from __future__ import annotations

from collections.abc import Callable

import pytest
from pydantic import SecretStr

from geoserver_mcp.adapters.geoserver_rest import GeoServerRestResult
from geoserver_mcp.config import BasicCredentials, RuntimeConfig, RuntimeInstanceConfig
from geoserver_mcp.domain import ReasonCode, ResponseStatus
from geoserver_mcp.services.inventory_service import list_instance_inventory


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
            RuntimeInstanceConfig(
                id="staging",
                base_url="https://staging.example.com/geoserver",
                data_directory=None,
                credentials=BasicCredentials(
                    username=SecretStr("staging-user"),
                    password=SecretStr("staging-password"),
                ),
            ),
        )
    )


class FakeGeoServerClient:
    def __init__(
        self,
        instance: RuntimeInstanceConfig,
        results: dict[str, GeoServerRestResult],
    ) -> None:
        self._instance = instance
        self._results = results

    async def get_connectivity_metadata(self) -> GeoServerRestResult:
        return self._results[self._instance.id]


def client_factory(
    results: dict[str, GeoServerRestResult],
) -> Callable[[RuntimeInstanceConfig], FakeGeoServerClient]:
    return lambda instance: FakeGeoServerClient(instance, results)


@pytest.mark.anyio
async def test_list_instance_inventory_returns_instance_summaries() -> None:
    results = {
        "production": GeoServerRestResult(
            status="success",
            data={"about": {"resource": [{"Version": "2.26.0"}]}},
            status_code=200,
            url="https://prod.example.com/geoserver/rest/about/version.json",
        ),
        "staging": GeoServerRestResult(
            status="failed",
            reason_code=ReasonCode.NETWORK_ERROR,
            message="staging-password failed",
            status_code=None,
            url=None,
        ),
    }

    response = await list_instance_inventory(
        runtime_config(),
        client_factory=client_factory(results),
    )
    serialized = str(response.model_dump(mode="json"))

    assert response.status == ResponseStatus.PARTIAL
    summaries = response.data["instances"]
    assert [summary.instance_id for summary in summaries] == ["production", "staging"]
    assert summaries[0].inspected_surfaces == ["geoserver_rest:about_version"]
    assert summaries[0].unavailable_information == []
    assert summaries[1].reason_code == ReasonCode.NETWORK_ERROR
    assert summaries[1].unavailable_information[0].reason_code == ReasonCode.NETWORK_ERROR
    assert "staging-password" not in serialized
