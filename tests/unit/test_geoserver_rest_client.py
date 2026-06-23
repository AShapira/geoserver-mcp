from __future__ import annotations

from typing import Any

import httpx
import pytest
import respx
from pydantic import SecretStr

from geoserver_mcp.adapters.geoserver_rest import GeoServerRestClient
from geoserver_mcp.config import BasicCredentials, RuntimeInstanceConfig
from geoserver_mcp.domain import ReasonCode


def runtime_instance() -> RuntimeInstanceConfig:
    return RuntimeInstanceConfig(
        id="production",
        base_url="https://geoserver.example.com/geoserver",
        data_directory=None,
        credentials=BasicCredentials(
            username=SecretStr("operator-user"),
            password=SecretStr("operator-password"),
        ),
    )


class CaptureTransport(httpx.AsyncBaseTransport):
    def __init__(self, response: httpx.Response) -> None:
        self.response = response
        self.requests: list[httpx.Request] = []

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return self.response


@pytest.mark.anyio
async def test_connectivity_request_uses_get_basic_auth_timeout_and_no_redirects() -> None:
    transport = CaptureTransport(httpx.Response(200, json={"about": {"resource": []}}))
    client = GeoServerRestClient(runtime_instance(), timeout_seconds=2.5, transport=transport)

    result = await client.get_json("rest/about/version.json")

    assert result.succeeded
    assert result.reason_code is None
    assert len(transport.requests) == 1
    request = transport.requests[0]
    assert request.method == "GET"
    assert str(request.url) == "https://geoserver.example.com/geoserver/rest/about/version.json"
    assert request.headers["authorization"].startswith("Basic ")
    assert client.timeout_seconds == 2.5
    assert client.follow_redirects is False


@pytest.mark.anyio
async def test_list_workspaces_uses_geoserver_rest_workspace_endpoint() -> None:
    transport = CaptureTransport(
        httpx.Response(200, json={"workspaces": {"workspace": [{"name": "topp"}]}})
    )
    client = GeoServerRestClient(runtime_instance(), transport=transport)

    result = await client.list_workspaces()

    assert result.succeeded
    assert len(transport.requests) == 1
    assert transport.requests[0].method == "GET"
    assert str(transport.requests[0].url) == (
        "https://geoserver.example.com/geoserver/rest/workspaces.json"
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "store_type, expected_endpoint",
    [
        ("data_stores", "datastores"),
        ("coverage_stores", "coveragestores"),
        ("wms_stores", "wmsstores"),
    ],
)
async def test_list_stores_uses_workspace_store_endpoints(
    store_type: str,
    expected_endpoint: str,
) -> None:
    transport = CaptureTransport(httpx.Response(200, json={"dataStores": {"dataStore": []}}))
    client = GeoServerRestClient(runtime_instance(), transport=transport)

    result = await client.list_stores("topp", store_type)

    assert result.succeeded
    assert len(transport.requests) == 1
    assert transport.requests[0].method == "GET"
    assert str(transport.requests[0].url) == (
        f"https://geoserver.example.com/geoserver/rest/workspaces/topp/{expected_endpoint}.json"
    )


@pytest.mark.anyio
async def test_list_stores_rejects_unsupported_store_type_before_network_access() -> None:
    transport = CaptureTransport(httpx.Response(200, json={"unexpected": True}))
    client = GeoServerRestClient(runtime_instance(), transport=transport)

    result = await client.list_stores("topp", "unknown")

    assert not result.succeeded
    assert result.reason_code == ReasonCode.UNSUPPORTED_ENDPOINT
    assert transport.requests == []


@pytest.mark.anyio
async def test_list_layers_uses_geoserver_rest_layers_endpoint() -> None:
    transport = CaptureTransport(httpx.Response(200, json={"layers": {"layer": []}}))
    client = GeoServerRestClient(runtime_instance(), transport=transport)

    result = await client.list_layers()

    assert result.succeeded
    assert len(transport.requests) == 1
    assert transport.requests[0].method == "GET"
    assert str(transport.requests[0].url) == (
        "https://geoserver.example.com/geoserver/rest/layers.json"
    )


@pytest.mark.anyio
async def test_list_layer_groups_uses_geoserver_rest_layergroups_endpoint() -> None:
    transport = CaptureTransport(httpx.Response(200, json={"layerGroups": {"layerGroup": []}}))
    client = GeoServerRestClient(runtime_instance(), transport=transport)

    result = await client.list_layer_groups()

    assert result.succeeded
    assert len(transport.requests) == 1
    assert transport.requests[0].method == "GET"
    assert str(transport.requests[0].url) == (
        "https://geoserver.example.com/geoserver/rest/layergroups.json"
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "target",
    [
        "https://evil.example.com/geoserver/rest/about/version.json",
        "//evil.example.com/geoserver/rest/about/version.json",
        "../admin",
        "rest/../admin",
        "rest/%2e%2e/admin",
        "rest/%2Fadmin",
        "rest/%5Cadmin",
    ],
)
async def test_unsafe_targets_are_rejected_before_network_access(target: str) -> None:
    transport = CaptureTransport(httpx.Response(200, json={"unexpected": True}))
    client = GeoServerRestClient(runtime_instance(), transport=transport)

    result = await client.get_json(target)

    assert not result.succeeded
    assert result.reason_code == ReasonCode.UNSUPPORTED_ENDPOINT
    assert transport.requests == []


@pytest.mark.anyio
@pytest.mark.parametrize(
    "status_code, reason_code",
    [
        (401, ReasonCode.AUTH_FAILED),
        (403, ReasonCode.FORBIDDEN),
        (404, ReasonCode.NOT_FOUND),
    ],
)
async def test_http_statuses_map_to_reason_codes(
    status_code: int,
    reason_code: ReasonCode,
) -> None:
    with respx.mock(base_url="https://geoserver.example.com") as router:
        router.get("/geoserver/rest/about/version.json").respond(status_code)
        client = GeoServerRestClient(runtime_instance())

        result = await client.get_json("rest/about/version.json")

    assert not result.succeeded
    assert result.reason_code == reason_code
    assert result.status_code == status_code


@pytest.mark.anyio
async def test_redirect_response_is_not_followed() -> None:
    with respx.mock(base_url="https://geoserver.example.com") as router:
        route = router.get("/geoserver/rest/about/version.json").respond(
            302,
            headers={"location": "https://evil.example.com/steal"},
        )
        client = GeoServerRestClient(runtime_instance())

        result = await client.get_json("rest/about/version.json")

    assert not result.succeeded
    assert result.reason_code == ReasonCode.UNSUPPORTED_ENDPOINT
    assert result.status_code == 302
    assert route.call_count == 1


@pytest.mark.anyio
async def test_timeout_maps_to_network_error() -> None:
    with respx.mock(base_url="https://geoserver.example.com") as router:
        router.get("/geoserver/rest/about/version.json").mock(
            side_effect=httpx.TimeoutException("operator-password timeout")
        )
        client = GeoServerRestClient(runtime_instance())

        result = await client.get_json("rest/about/version.json")

    assert not result.succeeded
    assert result.reason_code == ReasonCode.NETWORK_ERROR
    assert "operator-password" not in f"{result!r} {result.message}"


@pytest.mark.anyio
async def test_malformed_json_maps_to_parse_error() -> None:
    with respx.mock(base_url="https://geoserver.example.com") as router:
        router.get("/geoserver/rest/about/version.json").respond(200, text="{not-json")
        client = GeoServerRestClient(runtime_instance())

        result = await client.get_json("rest/about/version.json")

    assert not result.succeeded
    assert result.reason_code == ReasonCode.PARSE_ERROR
    assert result.status_code == 200


@pytest.mark.anyio
async def test_successful_json_response_is_redacted() -> None:
    with respx.mock(base_url="https://geoserver.example.com") as router:
        router.get("/geoserver/rest/about/version.json").respond(
            200,
            json={
                "username": "operator-user",
                "password": "operator-password",
                "version": "2.26.0",
            },
        )
        client = GeoServerRestClient(runtime_instance())

        result = await client.get_json("rest/about/version.json")

    assert result.succeeded
    assert result.data == {
        "username": "[REDACTED]",
        "password": "[REDACTED]",
        "version": "2.26.0",
    }


@pytest.mark.anyio
async def test_unexpected_exception_maps_to_unknown(monkeypatch) -> None:
    async def raise_unexpected(*args: Any, **kwargs: Any) -> httpx.Response:
        raise RuntimeError("operator-user unexpected")

    client = GeoServerRestClient(runtime_instance())
    monkeypatch.setattr(httpx.AsyncClient, "get", raise_unexpected)

    result = await client.get_json("rest/about/version.json")

    assert not result.succeeded
    assert result.reason_code == ReasonCode.UNKNOWN
    rendered = f"{result!r} {result.message}"
    assert "operator-user" not in rendered
    assert "operator-password" not in rendered
