# GeoServer MCP

GeoServer MCP is a Dockerized Model Context Protocol server for AI agents that need to inspect and manage GeoServer estates across multiple GeoServer instances.

The current server exposes read-only MCP inspection tools for configured GeoServer instances. It can check instance connectivity, report configured instance inventory, and list GeoServer workspaces, stores, layers, and layer groups across configured instances.

## Runtime

- Python: 3.13
- Package manager: uv
- MCP SDK: official Python package `mcp`
- Default container transport: Streamable HTTP on port `8000`

## Local Development

Install `uv`, then run:

```powershell
uv sync --frozen
uv run pytest
uv run ruff check --no-cache .
uv run ruff format --check --no-cache .
docker build --tag geoserver-mcp:dev .
```

The same core checks run in CI.

Type checking is intentionally deferred until Story 1.2 introduces the first configuration model and typed runtime boundary. TODO owner: maintainer.

## Docker

Build the image:

```powershell
docker build --tag geoserver-mcp:dev .
```

Run with Docker Compose:

```powershell
docker compose up --build
```

The image runs as a non-root user and starts the package entrypoint. GeoServer configuration is optional at process construction time; configured inspection tools are registered when runtime config is supplied.

## Local GeoServer Fixture

The repository includes a local-test-only GeoServer fixture behind the `fixture` Docker Compose profile. It uses a pinned OSGeo GeoServer image and exposes GeoServer on `127.0.0.1:8080`.

Start the fixture:

```powershell
docker compose --profile fixture up geoserver-fixture
```

Run the gated integration test from another shell after GeoServer is ready:

```powershell
$env:GEOSERVER_MCP_RUN_FIXTURE_TESTS = "1"
$env:GEOSERVER_FIXTURE_USER = "admin"
$env:GEOSERVER_FIXTURE_PASSWORD = "geoserver"
$env:GEOSERVER_FIXTURE_URL = "http://localhost:8080/geoserver"
uv run pytest tests/integration/test_check_instances_geoserver_fixture.py
```

The `admin` / `geoserver` credentials are only for the local Docker fixture. Do not use default GeoServer credentials in production configuration. Production examples continue to use environment variable references and placeholder values.

Use `http://localhost:8080/geoserver` for integration tests running on the host. Use `http://geoserver-fixture:8080/geoserver` only from containers attached to the same Compose network.

## Configuration

GeoServer instances are described in a YAML config file. Credentials are referenced by environment variable name so secret values do not need to be written into the config file.

```yaml
instances:
  - id: production
    base_url: https://geoserver.example.com/geoserver
    auth:
      type: basic
      username_env: GEOSERVER_PROD_USER
      password_env: GEOSERVER_PROD_PASSWORD
```

See `examples/geoserver-mcp.yaml` and `examples/geoserver-mcp.env.example` for a two-instance example. Config loading validates required fields, duplicate instance IDs, and HTTP/HTTPS base URLs before any GeoServer network calls can be made. Secret values are redacted from normal displays, validation errors, and runtime credential representations.

See `examples/geoserver-mcp.fixture.yaml` and `examples/geoserver-mcp.fixture.env.example` only for the local Docker fixture.

## MCP Tools

- `check_instances`: checks all configured GeoServer instances for reachability, authentication, and basic version metadata.
- `list_catalog`: returns catalog inventory for a requested resource type. Supported `resource_types` are currently `["instances"]`, `["workspaces"]`, `["stores"]`, and `["layers"]`.

All v1 tools are read-only. Create, update, delete, reload, purge, and other GeoServer mutation actions are unsupported in v1.
