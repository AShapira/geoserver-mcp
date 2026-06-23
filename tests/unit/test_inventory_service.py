from __future__ import annotations

from collections.abc import Callable

import pytest
from pydantic import SecretStr

from geoserver_mcp.adapters.geoserver_rest import GeoServerRestResult
from geoserver_mcp.config import BasicCredentials, RuntimeConfig, RuntimeInstanceConfig
from geoserver_mcp.domain import ReasonCode, ResponseStatus
from geoserver_mcp.services.inventory_service import (
    list_instance_inventory,
    list_layer_inventory,
    list_store_inventory,
    list_workspace_inventory,
)


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

    async def list_workspaces(self) -> GeoServerRestResult:
        return self._results[self._instance.id]


def client_factory(
    results: dict[str, GeoServerRestResult],
) -> Callable[[RuntimeInstanceConfig], FakeGeoServerClient]:
    return lambda instance: FakeGeoServerClient(instance, results)


class FakeStoreClient:
    def __init__(
        self,
        instance: RuntimeInstanceConfig,
        workspace_results: dict[str, GeoServerRestResult],
        store_results: dict[tuple[str, str, str], GeoServerRestResult],
    ) -> None:
        self._instance = instance
        self._workspace_results = workspace_results
        self._store_results = store_results

    async def list_workspaces(self) -> GeoServerRestResult:
        return self._workspace_results[self._instance.id]

    async def list_stores(self, workspace: str, store_type: str) -> GeoServerRestResult:
        return self._store_results[(self._instance.id, workspace, store_type)]


def store_client_factory(
    workspace_results: dict[str, GeoServerRestResult],
    store_results: dict[tuple[str, str, str], GeoServerRestResult],
) -> Callable[[RuntimeInstanceConfig], FakeStoreClient]:
    return lambda instance: FakeStoreClient(instance, workspace_results, store_results)


class FakeLayerClient:
    def __init__(
        self,
        instance: RuntimeInstanceConfig,
        layer_results: dict[str, GeoServerRestResult],
        layer_group_results: dict[str, GeoServerRestResult],
    ) -> None:
        self._instance = instance
        self._layer_results = layer_results
        self._layer_group_results = layer_group_results

    async def list_layers(self) -> GeoServerRestResult:
        return self._layer_results[self._instance.id]

    async def list_layer_groups(self) -> GeoServerRestResult:
        return self._layer_group_results[self._instance.id]


def layer_client_factory(
    layer_results: dict[str, GeoServerRestResult],
    layer_group_results: dict[str, GeoServerRestResult],
) -> Callable[[RuntimeInstanceConfig], FakeLayerClient]:
    return lambda instance: FakeLayerClient(instance, layer_results, layer_group_results)


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


@pytest.mark.anyio
async def test_list_workspace_inventory_returns_workspaces_across_instances() -> None:
    results = {
        "production": GeoServerRestResult(
            status="success",
            data={
                "workspaces": {
                    "workspace": [
                        {
                            "name": "topp",
                            "href": "https://prod.example.com/geoserver/rest/workspaces/topp.json",
                        },
                        {"name": "nurc"},
                    ]
                }
            },
            status_code=200,
            url="https://prod.example.com/geoserver/rest/workspaces.json",
        ),
        "staging": GeoServerRestResult(
            status="failed",
            reason_code=ReasonCode.AUTH_FAILED,
            message="staging-password failed",
            status_code=401,
            url="https://staging.example.com/geoserver/rest/workspaces.json",
        ),
    }

    response = await list_workspace_inventory(
        runtime_config(),
        client_factory=client_factory(results),
    )
    serialized = str(response.model_dump(mode="json"))

    assert response.status == ResponseStatus.PARTIAL
    assert [workspace.name for workspace in response.data["workspaces"]] == ["topp", "nurc"]
    assert response.data["workspaces"][0].instance_id == "production"
    assert response.data["workspaces"][0].resource_id == "topp"
    assert response.errors[0].instance_id == "staging"
    assert response.errors[0].reason_code == ReasonCode.AUTH_FAILED
    assert response.metadata["resource_types"] == ["workspaces"]
    assert "staging-password" not in serialized


@pytest.mark.anyio
async def test_list_workspace_inventory_maps_malformed_workspace_response_to_parse_error() -> None:
    results = {
        "production": GeoServerRestResult(
            status="success",
            data={"unexpected": []},
            status_code=200,
            url="https://prod.example.com/geoserver/rest/workspaces.json",
        ),
        "staging": GeoServerRestResult(
            status="success",
            data={"workspaces": {"workspace": []}},
            status_code=200,
            url="https://staging.example.com/geoserver/rest/workspaces.json",
        ),
    }

    response = await list_workspace_inventory(
        runtime_config(),
        client_factory=client_factory(results),
    )

    assert response.status == ResponseStatus.PARTIAL
    assert response.data["workspaces"] == []
    assert response.errors[0].instance_id == "production"
    assert response.errors[0].reason_code == ReasonCode.PARSE_ERROR


@pytest.mark.anyio
async def test_list_store_inventory_returns_redacted_stores_across_workspaces() -> None:
    workspace_results = {
        "production": GeoServerRestResult(
            status="success",
            data={"workspaces": {"workspace": [{"name": "topp"}]}},
            status_code=200,
            url="https://prod.example.com/geoserver/rest/workspaces.json",
        ),
        "staging": GeoServerRestResult(
            status="success",
            data={"workspaces": {"workspace": [{"name": "nurc"}]}},
            status_code=200,
            url="https://staging.example.com/geoserver/rest/workspaces.json",
        ),
    }
    store_results = {
        (
            "production",
            "topp",
            "data_stores",
        ): GeoServerRestResult(
            status="success",
            data={
                "dataStores": {
                    "dataStore": [
                        {
                            "name": "roads",
                            "href": "https://prod.example.com/geoserver/rest/workspaces/topp/datastores/roads.json?password=prod-password",
                            "enabled": True,
                            "password": "prod-password",
                        }
                    ]
                }
            },
            status_code=200,
            url="https://prod.example.com/geoserver/rest/workspaces/topp/datastores.json",
        ),
        ("production", "topp", "coverage_stores"): GeoServerRestResult(
            status="success",
            data={"coverageStores": {"coverageStore": [{"name": "dem", "enabled": False}]}},
            status_code=200,
            url="https://prod.example.com/geoserver/rest/workspaces/topp/coveragestores.json",
        ),
        ("production", "topp", "wms_stores"): GeoServerRestResult(
            status="success",
            data={"wmsStores": {"wmsStore": []}},
            status_code=200,
            url="https://prod.example.com/geoserver/rest/workspaces/topp/wmsstores.json",
        ),
        ("staging", "nurc", "data_stores"): GeoServerRestResult(
            status="failed",
            reason_code=ReasonCode.FORBIDDEN,
            message="staging-password forbidden",
            status_code=403,
            url="https://staging.example.com/geoserver/rest/workspaces/nurc/datastores.json",
        ),
        ("staging", "nurc", "coverage_stores"): GeoServerRestResult(
            status="success",
            data={"coverageStores": {"coverageStore": []}},
            status_code=200,
            url="https://staging.example.com/geoserver/rest/workspaces/nurc/coveragestores.json",
        ),
        ("staging", "nurc", "wms_stores"): GeoServerRestResult(
            status="success",
            data={"wmsStores": {"wmsStore": []}},
            status_code=200,
            url="https://staging.example.com/geoserver/rest/workspaces/nurc/wmsstores.json",
        ),
    }

    response = await list_store_inventory(
        runtime_config(),
        client_factory=store_client_factory(workspace_results, store_results),
    )
    serialized = str(response.model_dump(mode="json"))

    assert response.status == ResponseStatus.PARTIAL
    stores = response.data["stores"]
    assert [(store.workspace, store.name, store.store_type) for store in stores] == [
        ("topp", "roads", "data_stores"),
        ("topp", "dem", "coverage_stores"),
    ]
    assert stores[0].resource_id == "topp:roads"
    assert stores[0].enabled is True
    assert stores[1].enabled is False
    assert response.errors[0].instance_id == "staging"
    assert response.errors[0].reason_code == ReasonCode.FORBIDDEN
    assert response.metadata["resource_types"] == ["stores"]
    assert "prod-password" not in serialized
    assert "staging-password" not in serialized


@pytest.mark.anyio
async def test_list_store_inventory_maps_malformed_store_response_to_parse_error() -> None:
    workspace_results = {
        "production": GeoServerRestResult(
            status="success",
            data={"workspaces": {"workspace": [{"name": "topp"}]}},
            status_code=200,
            url="https://prod.example.com/geoserver/rest/workspaces.json",
        ),
        "staging": GeoServerRestResult(
            status="failed",
            reason_code=ReasonCode.NETWORK_ERROR,
            message="network failed",
        ),
    }
    store_results = {
        ("production", "topp", "data_stores"): GeoServerRestResult(
            status="success",
            data={"unexpected": []},
            status_code=200,
            url="https://prod.example.com/geoserver/rest/workspaces/topp/datastores.json",
        ),
        ("production", "topp", "coverage_stores"): GeoServerRestResult(
            status="success",
            data={"coverageStores": {"coverageStore": []}},
            status_code=200,
            url="https://prod.example.com/geoserver/rest/workspaces/topp/coveragestores.json",
        ),
        ("production", "topp", "wms_stores"): GeoServerRestResult(
            status="success",
            data={"wmsStores": {"wmsStore": []}},
            status_code=200,
            url="https://prod.example.com/geoserver/rest/workspaces/topp/wmsstores.json",
        ),
    }

    response = await list_store_inventory(
        runtime_config(),
        client_factory=store_client_factory(workspace_results, store_results),
    )

    assert response.status == ResponseStatus.PARTIAL
    assert response.errors[0].instance_id == "production"
    assert response.errors[0].reason_code == ReasonCode.PARSE_ERROR
    assert response.errors[1].instance_id == "staging"
    assert response.errors[1].reason_code == ReasonCode.NETWORK_ERROR


@pytest.mark.anyio
async def test_list_layer_inventory_returns_layers_and_layer_groups() -> None:
    layer_results = {
        "production": GeoServerRestResult(
            status="success",
            data={
                "layers": {
                    "layer": [
                        {
                            "name": "topp:states",
                            "href": "https://prod.example.com/geoserver/rest/layers/topp:states.json?password=prod-password",
                            "type": "VECTOR",
                            "enabled": True,
                            "advertised": False,
                            "defaultStyle": {"name": "polygon"},
                            "resource": {"name": "states", "@class": "featureType"},
                            "store": {"name": "states_store"},
                        },
                        "nurc:Img_Sample",
                    ]
                }
            },
            status_code=200,
            url="https://prod.example.com/geoserver/rest/layers.json",
        ),
        "staging": GeoServerRestResult(
            status="failed",
            reason_code=ReasonCode.AUTH_FAILED,
            message="staging-password failed",
            status_code=401,
            url="https://staging.example.com/geoserver/rest/layers.json",
        ),
    }
    layer_group_results = {
        "production": GeoServerRestResult(
            status="success",
            data={
                "layerGroups": {
                    "layerGroup": [
                        {
                            "name": "basemap",
                            "workspace": {"name": "topp"},
                            "layers": {
                                "layer": [
                                    {"name": "topp:states"},
                                    {"name": "nurc:Img_Sample"},
                                ]
                            },
                            "href": "https://prod.example.com/geoserver/rest/layergroups/basemap.json",
                        }
                    ]
                }
            },
            status_code=200,
            url="https://prod.example.com/geoserver/rest/layergroups.json",
        ),
        "staging": GeoServerRestResult(
            status="success",
            data={"layerGroups": {"layerGroup": []}},
            status_code=200,
            url="https://staging.example.com/geoserver/rest/layergroups.json",
        ),
    }

    response = await list_layer_inventory(
        runtime_config(),
        client_factory=layer_client_factory(layer_results, layer_group_results),
    )
    serialized = str(response.model_dump(mode="json"))

    assert response.status == ResponseStatus.PARTIAL
    layers = response.data["layers"]
    assert [(layer.name, layer.workspace, layer.resource_id) for layer in layers] == [
        ("topp:states", "topp", "topp:states"),
        ("nurc:Img_Sample", "nurc", "nurc:Img_Sample"),
    ]
    assert layers[0].resource_type == "VECTOR"
    assert layers[0].enabled is True
    assert layers[0].advertised is False
    assert layers[0].default_style == "polygon"
    assert layers[0].resource == "states"
    assert layers[0].store == "states_store"
    assert response.data["layer_groups"][0].resource_id == "topp:basemap"
    assert response.data["layer_groups"][0].layers == ["topp:states", "nurc:Img_Sample"]
    assert response.errors[0].instance_id == "staging"
    assert response.errors[0].reason_code == ReasonCode.AUTH_FAILED
    assert response.metadata["resource_types"] == ["layers"]
    assert "prod-password" not in serialized
    assert "staging-password" not in serialized


@pytest.mark.anyio
async def test_list_layer_inventory_adds_warning_for_malformed_related_resource() -> None:
    layer_results = {
        "production": GeoServerRestResult(
            status="success",
            data={"layers": {"layer": [{"name": "topp:broken", "resource": {}}]}},
            status_code=200,
            url="https://prod.example.com/geoserver/rest/layers.json",
        ),
        "staging": GeoServerRestResult(
            status="success",
            data={"layers": {"layer": []}},
            status_code=200,
            url="https://staging.example.com/geoserver/rest/layers.json",
        ),
    }
    layer_group_results = {
        "production": GeoServerRestResult(
            status="success",
            data={"layerGroups": {"layerGroup": []}},
            status_code=200,
            url="https://prod.example.com/geoserver/rest/layergroups.json",
        ),
        "staging": GeoServerRestResult(
            status="success",
            data={"layerGroups": {"layerGroup": []}},
            status_code=200,
            url="https://staging.example.com/geoserver/rest/layergroups.json",
        ),
    }

    response = await list_layer_inventory(
        runtime_config(),
        client_factory=layer_client_factory(layer_results, layer_group_results),
    )

    assert response.status == ResponseStatus.SUCCESS
    assert response.data["layers"][0].name == "topp:broken"
    assert response.findings == [
        {
            "severity": "warning",
            "reason_code": "partial_result",
            "instance_id": "production",
            "resource": {"type": "layer", "name": "topp:broken"},
            "message": "Layer related resource metadata was unavailable or malformed.",
            "suggested_next_step": "Inspect catalog resource detail when that story is available.",
        }
    ]


@pytest.mark.anyio
async def test_list_layer_inventory_maps_malformed_layer_response_to_parse_error() -> None:
    layer_results = {
        "production": GeoServerRestResult(
            status="success",
            data={"unexpected": []},
            status_code=200,
            url="https://prod.example.com/geoserver/rest/layers.json",
        ),
        "staging": GeoServerRestResult(
            status="success",
            data={"layers": {"layer": []}},
            status_code=200,
            url="https://staging.example.com/geoserver/rest/layers.json",
        ),
    }
    layer_group_results = {
        "production": GeoServerRestResult(
            status="success",
            data={"layerGroups": {"layerGroup": []}},
            status_code=200,
            url="https://prod.example.com/geoserver/rest/layergroups.json",
        ),
        "staging": GeoServerRestResult(
            status="success",
            data={"layerGroups": {"layerGroup": []}},
            status_code=200,
            url="https://staging.example.com/geoserver/rest/layergroups.json",
        ),
    }

    response = await list_layer_inventory(
        runtime_config(),
        client_factory=layer_client_factory(layer_results, layer_group_results),
    )

    assert response.status == ResponseStatus.PARTIAL
    assert response.errors[0].instance_id == "production"
    assert response.errors[0].reason_code == ReasonCode.PARSE_ERROR


@pytest.mark.anyio
async def test_list_layer_inventory_warns_for_malformed_layer_and_group_entries() -> None:
    layer_results = {
        "production": GeoServerRestResult(
            status="success",
            data={"layers": {"layer": [{"href": "https://prod.example.com/no-name"}]}},
            status_code=200,
            url="https://prod.example.com/geoserver/rest/layers.json",
        ),
        "staging": GeoServerRestResult(
            status="success",
            data={"layers": {"layer": []}},
            status_code=200,
            url="https://staging.example.com/geoserver/rest/layers.json",
        ),
    }
    layer_group_results = {
        "production": GeoServerRestResult(
            status="success",
            data={"layerGroups": {"layerGroup": [{"href": "https://prod.example.com/no-name"}]}},
            status_code=200,
            url="https://prod.example.com/geoserver/rest/layergroups.json",
        ),
        "staging": GeoServerRestResult(
            status="success",
            data={"layerGroups": {"layerGroup": []}},
            status_code=200,
            url="https://staging.example.com/geoserver/rest/layergroups.json",
        ),
    }

    response = await list_layer_inventory(
        runtime_config(),
        client_factory=layer_client_factory(layer_results, layer_group_results),
    )

    assert response.status == ResponseStatus.SUCCESS
    assert response.data["layers"] == []
    assert response.data["layer_groups"] == []
    assert [
        (finding["resource"]["type"], finding["resource"]["name"]) for finding in response.findings
    ] == [
        ("layer", "entry[0]"),
        ("layer_group", "entry[0]"),
    ]


@pytest.mark.anyio
async def test_list_layer_inventory_warns_for_malformed_layer_group_membership() -> None:
    layer_results = {
        "production": GeoServerRestResult(
            status="success",
            data={"layers": {"layer": []}},
            status_code=200,
            url="https://prod.example.com/geoserver/rest/layers.json",
        ),
        "staging": GeoServerRestResult(
            status="success",
            data={"layers": {"layer": []}},
            status_code=200,
            url="https://staging.example.com/geoserver/rest/layers.json",
        ),
    }
    layer_group_results = {
        "production": GeoServerRestResult(
            status="success",
            data={
                "layerGroups": {"layerGroup": [{"name": "broken", "layers": {"unexpected": []}}]}
            },
            status_code=200,
            url="https://prod.example.com/geoserver/rest/layergroups.json",
        ),
        "staging": GeoServerRestResult(
            status="success",
            data={"layerGroups": {"layerGroup": []}},
            status_code=200,
            url="https://staging.example.com/geoserver/rest/layergroups.json",
        ),
    }

    response = await list_layer_inventory(
        runtime_config(),
        client_factory=layer_client_factory(layer_results, layer_group_results),
    )

    assert response.status == ResponseStatus.SUCCESS
    assert response.data["layer_groups"][0].name == "broken"
    assert response.data["layer_groups"][0].layers == []
    assert response.findings[0]["resource"] == {"type": "layer_group", "name": "broken"}
    assert response.findings[0]["message"] == (
        "Layer-group membership metadata was unavailable or malformed."
    )


@pytest.mark.anyio
async def test_list_layer_inventory_redacts_href_query_secrets_and_group_workspace() -> None:
    layer_results = {
        "production": GeoServerRestResult(
            status="success",
            data={
                "layers": {
                    "layer": [
                        {
                            "name": "states",
                            "href": "https://prod.example.com/geoserver/rest/layers/states.json?token=abc123&format=json",
                        }
                    ]
                }
            },
            status_code=200,
            url="https://prod.example.com/geoserver/rest/layers.json",
        ),
        "staging": GeoServerRestResult(
            status="success",
            data={"layers": {"layer": []}},
            status_code=200,
            url="https://staging.example.com/geoserver/rest/layers.json",
        ),
    }
    layer_group_results = {
        "production": GeoServerRestResult(
            status="success",
            data={
                "layerGroups": {
                    "layerGroup": [
                        {
                            "name": "basemap",
                            "href": "https://prod.example.com/geoserver/rest/workspaces/topp/layergroups/basemap.json?password=hidden",
                        }
                    ]
                }
            },
            status_code=200,
            url="https://prod.example.com/geoserver/rest/layergroups.json",
        ),
        "staging": GeoServerRestResult(
            status="success",
            data={"layerGroups": {"layerGroup": []}},
            status_code=200,
            url="https://staging.example.com/geoserver/rest/layergroups.json",
        ),
    }

    response = await list_layer_inventory(
        runtime_config(),
        client_factory=layer_client_factory(layer_results, layer_group_results),
    )
    serialized = str(response.model_dump(mode="json"))

    assert response.status == ResponseStatus.SUCCESS
    assert "abc123" not in serialized
    assert "hidden" not in serialized
    assert "token=[REDACTED]" in serialized
    assert "password=[REDACTED]" in serialized
    assert response.data["layer_groups"][0].workspace == "topp"
    assert response.data["layer_groups"][0].resource_id == "topp:basemap"
