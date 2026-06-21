# GeoServer MCP

GeoServer MCP is a Dockerized Model Context Protocol server for AI agents that need to inspect and manage GeoServer estates across multiple GeoServer instances.

This repository is currently at the initial scaffold stage. The server starts without GeoServer configuration and does not make GeoServer network calls yet.

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

The scaffold image runs as a non-root user and starts the package entrypoint. No GeoServer credentials, data directories, or instance configuration are required for this story.

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
