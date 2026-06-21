from __future__ import annotations

from collections.abc import Callable

import pytest
from pydantic import SecretStr

from geoserver_mcp.adapters.geoserver_rest import GeoServerRestResult
from geoserver_mcp.config import BasicCredentials, RuntimeConfig, RuntimeInstanceConfig
from geoserver_mcp.domain import ReasonCode, ResponseStatus
from geoserver_mcp.services.instance_service import check_instances


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
        calls: list[str],
    ) -> None:
        self._instance = instance
        self._results = results
        self._calls = calls

    async def get_connectivity_metadata(self) -> GeoServerRestResult:
        self._calls.append(self._instance.id)
        return self._results[self._instance.id]


class RaisingGeoServerClient:
    def __init__(self, instance: RuntimeInstanceConfig, calls: list[str]) -> None:
        self._instance = instance
        self._calls = calls

    async def get_connectivity_metadata(self) -> GeoServerRestResult:
        self._calls.append(self._instance.id)
        if self._instance.id == "production":
            raise RuntimeError("prod-password exploded")
        return GeoServerRestResult(
            status="success",
            data={"about": {"resource": [{"Version": "2.26.0"}]}},
            status_code=200,
            url="https://staging.example.com/geoserver/rest/about/version.json",
        )


def client_factory(
    results: dict[str, GeoServerRestResult],
    calls: list[str],
) -> Callable[[RuntimeInstanceConfig], FakeGeoServerClient]:
    return lambda instance: FakeGeoServerClient(instance, results, calls)


@pytest.mark.anyio
async def test_check_instances_returns_all_instances_with_partial_status() -> None:
    calls: list[str] = []
    results = {
        "production": GeoServerRestResult(
            status="success",
            data={"about": {"resource": [{"@name": "GeoServer", "Version": "2.26.0"}]}},
            status_code=200,
            url="https://prod.example.com/geoserver/rest/about/version.json",
        ),
        "staging": GeoServerRestResult(
            status="failed",
            reason_code=ReasonCode.AUTH_FAILED,
            message="GeoServer authentication failed",
            status_code=401,
            url="https://staging.example.com/geoserver/rest/about/version.json",
        ),
    }

    response = await check_instances(
        runtime_config(),
        client_factory=client_factory(results, calls),
    )

    assert response.status == ResponseStatus.PARTIAL
    assert calls == ["production", "staging"]
    instances = response.data["instances"]
    assert [item.instance_id for item in instances] == ["production", "staging"]
    assert instances[0].reachable is True
    assert instances[0].authenticated is True
    assert instances[0].server_version == "2.26.0"
    assert instances[1].reachable is True
    assert instances[1].authenticated is False
    assert instances[1].reason_code == ReasonCode.AUTH_FAILED
    assert response.errors[0].instance_id == "staging"
    assert response.errors[0].reason_code == ReasonCode.AUTH_FAILED


@pytest.mark.anyio
@pytest.mark.parametrize(
    "reason_code",
    [
        ReasonCode.NETWORK_ERROR,
        ReasonCode.FORBIDDEN,
        ReasonCode.UNSUPPORTED_ENDPOINT,
        ReasonCode.UNKNOWN,
    ],
)
async def test_check_instances_preserves_failure_reason_codes(reason_code: ReasonCode) -> None:
    calls: list[str] = []
    results = {
        "production": GeoServerRestResult(
            status="failed",
            reason_code=reason_code,
            message="redacted failure",
            status_code=None,
            url=None,
        ),
        "staging": GeoServerRestResult(
            status="failed",
            reason_code=reason_code,
            message="redacted failure",
            status_code=None,
            url=None,
        ),
    }

    response = await check_instances(
        runtime_config(),
        client_factory=client_factory(results, calls),
    )

    assert response.status == ResponseStatus.FAILED
    assert {error.reason_code for error in response.errors} == {reason_code}
    assert [item.reason_code for item in response.data["instances"]] == [reason_code, reason_code]


@pytest.mark.anyio
async def test_check_instances_serialization_redacts_secrets() -> None:
    calls: list[str] = []
    results = {
        "production": GeoServerRestResult(
            status="failed",
            reason_code=ReasonCode.NETWORK_ERROR,
            message="prod-password failed",
            status_code=None,
            url=None,
        ),
        "staging": GeoServerRestResult(
            status="success",
            data={"about": {"resource": [{"Version": "staging-password"}]}},
            status_code=200,
            url="https://staging.example.com/geoserver/rest/about/version.json",
        ),
    }

    response = await check_instances(
        runtime_config(),
        client_factory=client_factory(results, calls),
    )
    serialized = str(response.model_dump(mode="json"))

    assert "prod-password" not in serialized
    assert "staging-password" not in serialized
    assert "[REDACTED]" in serialized


@pytest.mark.anyio
async def test_check_instances_isolates_unexpected_client_exceptions() -> None:
    calls: list[str] = []

    response = await check_instances(
        runtime_config(),
        client_factory=lambda instance: RaisingGeoServerClient(instance, calls),
    )
    serialized = str(response.model_dump(mode="json"))

    assert response.status == ResponseStatus.PARTIAL
    assert calls == ["production", "staging"]
    assert response.data["instances"][0].reason_code == ReasonCode.UNKNOWN
    assert response.data["instances"][1].server_version == "2.26.0"
    assert "prod-password" not in serialized
