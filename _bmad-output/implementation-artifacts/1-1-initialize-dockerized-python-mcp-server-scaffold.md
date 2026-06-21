# Story 1.1: Initialize Dockerized Python MCP Server Scaffold

Status: done

## Story

As a GeoServer MCP maintainer,
I want a Python package and Docker runtime scaffold,
so that the server can start consistently as the foundation for all future capabilities.

## Acceptance Criteria

1. Given the repository is empty except for BMAD artifacts, when the scaffold is initialized, then the project contains a `uv`-managed Python package using the approved `src/geoserver_mcp/` layout, and the package exposes a `geoserver-mcp` entrypoint that starts without GeoServer configuration.
2. Given the Docker runtime is built, when the container starts with minimal valid runtime settings, then the MCP server process starts successfully, the image runs as a non-root user, and the Dockerfile uses a pinned Python base image.
3. Given tests are run, when the scaffold test suite executes, then at least one smoke test proves the package imports and server app can be constructed.
4. Given the initial scaffold is created, when repository quality checks are run, then the project exposes a documented single command or small command set for running tests and code quality checks, the checks include the scaffold smoke test, and formatting, linting, and type-checking expectations are documented or explicitly deferred.
5. Given the Docker runtime is part of the scaffold, when the quality gate runs locally or in CI, then the Docker image build is verified and failures stop the quality gate with actionable output.
6. Given the repository is ready for collaborative implementation, when CI configuration is inspected, then an initial CI workflow exists or the story explicitly documents why CI is deferred, and the CI/local quality gate runs the same core checks used by developers.

## Tasks / Subtasks

- [x] Initialize the Python package scaffold safely in the existing repo. (AC: 1)
  - [x] Run or reproduce the result of `uv init --package --name geoserver-mcp` in the repository root without deleting or overwriting BMAD artifacts.
  - [x] If `uv init` refuses because generated files already exist, initialize in a temporary directory and copy only the intended scaffold files.
  - [x] Ensure package import path is `src/geoserver_mcp/`, not `geoserver-mcp/`.
  - [x] Create or preserve `pyproject.toml`, `.python-version`, `README.md`, and `uv.lock`.
- [x] Add the minimum MCP server application skeleton. (AC: 1, 3)
  - [x] Add `src/geoserver_mcp/__init__.py`, `src/geoserver_mcp/__main__.py`, and `src/geoserver_mcp/server.py`.
  - [x] Add an app factory that can be imported and constructed without GeoServer configuration.
  - [x] Expose the package script `geoserver-mcp` from `pyproject.toml`.
  - [x] Do not implement `check_instances` in this story; that belongs to Story 1.4.
- [x] Create the initial architectural directory skeleton. (AC: 1)
  - [x] Create package directories from the architecture: `config/`, `domain/`, `services/`, `adapters/mcp/`, `adapters/geoserver_rest/`, `adapters/ogc/`, `adapters/data_directory/`, `diagnostics/`, `reporting/`, `security/`, and `observability/`.
  - [x] Add `__init__.py` files so the package imports cleanly.
  - [x] Keep modules mostly empty unless needed for the import/app smoke test.
- [x] Add Python dependencies and quality tooling. (AC: 3, 4, 6)
  - [x] Use Python 3.13 for v1.
  - [x] Add runtime dependency on the official Python MCP SDK package `mcp`.
  - [x] Add development dependencies for `pytest` and `ruff`.
  - [x] Add `pyproject.toml` configuration for Ruff lint/format if using Ruff.
  - [x] Document the local quality command set in `README.md`, for example `uv run pytest`, `uv run ruff check .`, and `uv run ruff format --check .`.
- [x] Add smoke tests. (AC: 3, 4)
  - [x] Add `tests/unit/test_scaffold.py`.
  - [x] Test that `geoserver_mcp` imports.
  - [x] Test that the server app factory can be constructed without GeoServer config.
  - [x] Test or verify the package entrypoint starts far enough to prove wiring without requiring real GeoServer access.
- [x] Add Docker runtime scaffold. (AC: 2, 5)
  - [x] Add `.dockerignore`.
  - [x] Add `Dockerfile` using a pinned Python 3.13 slim base image.
  - [x] Run the container process as a non-root user with an explicit UID/GID.
  - [x] Ensure the image starts the package entrypoint rather than a loose script.
  - [x] Add the minimum `docker-compose.yml` needed to build and start the MCP server container; GeoServer fixture services are Story 1.6 unless a tiny placeholder is needed for developer ergonomics.
- [x] Add CI quality gate. (AC: 4, 5, 6)
  - [x] Add `.github/workflows/ci.yml`.
  - [x] CI must install/sync dependencies with `uv`, run the same local quality commands documented in `README.md`, and build the Docker image.
  - [x] If any check is intentionally deferred, document the deferral in `README.md` with a clear reason and TODO owner.
- [x] Verify and update sprint tracking. (AC: all)
  - [x] Run the documented local quality command set.
  - [x] Run Docker image build.
  - [x] Confirm no secrets, `.env`, local data directories, or generated runtime logs are tracked.
  - [x] Leave `_bmad-output/implementation-artifacts/sprint-status.yaml` with this story as `ready-for-dev` until development starts.

### Review Findings

- [x] [Review][Patch] CI references an unresolved `astral-sh/setup-uv@v8` ref [.github/workflows/ci.yml:24]
- [x] [Review][Patch] MCP SDK import bypasses the required `adapters/mcp` boundary [src/geoserver_mcp/server.py:5]
- [x] [Review][Patch] Env-driven CLI defaults can bypass controlled argparse validation [src/geoserver_mcp/__main__.py:15]
- [x] [Review][Patch] CI builds the Docker image but never exercises the container startup path [.github/workflows/ci.yml:41]
- [x] [Review][Patch] Compose publishes the MCP server on all host interfaces by default [docker-compose.yml:10]

## Dev Notes

### Source Context

- Story source: [epics.md](../planning-artifacts/epics.md) Story 1.1 and Epic 1.
- PRD source: [prd.md](../planning-artifacts/prds/prd-geoserver-mcp-2026-05-25/prd.md) FR-1, FR-17, FR-18, FR-19, NFR-1, NFR-2, NFR-7, MVP scope, and guardrails.
- Architecture source: [architecture.md](../planning-artifacts/architecture.md) starter template, core decisions, implementation patterns, project structure, and implementation handoff.

### Architecture Requirements

- Use a custom `uv init --package --name geoserver-mcp` package scaffold as the base. The uv docs state that `--package` creates a packaged application with `src/<module>/`, a build system, and a script entry point. Current uv docs also note that `uv init` exits if a target already has `pyproject.toml`; handle this safely in the existing repo. Source: https://docs.astral.sh/uv/concepts/projects/init/
- Use Python 3.13 for v1. As of the current docs check, Python 3.13 is still a stable Python documentation line, while Python 3.14 is also stable; the project architecture intentionally selects 3.13 to reduce dependency ecosystem risk. Source: https://docs.python.org/3.13/
- Use the official Python MCP SDK package `mcp` / FastMCP, not the separate third-party FastMCP 2 package, unless a later architecture decision changes this. Current PyPI check found `mcp` 1.27.1 uploaded May 8, 2026. Source: https://pypi.org/project/mcp/
- The scaffold must use the architecture's `src/geoserver_mcp/` package layout and boundaries:
  - `adapters/mcp/` is the only place that may import MCP SDK types.
  - `adapters/geoserver_rest/` will later own GeoServer REST HTTP code.
  - `adapters/ogc/` will later own OGC parsing.
  - `adapters/data_directory/` will later own optional filesystem inspection.
  - `domain/`, `services/`, `diagnostics/`, `reporting/`, `security/`, and `observability/` must stay independent of MCP SDK specifics.
- V1 is read-only. Do not add mutation tools, write endpoints, reload/purge/cache-clear operations, or generic HTTP proxy behavior.
- Do not add a database, queue, event system, background worker, web UI, dashboard, Kubernetes deployment, or direct PostGIS access.
- No raw GeoServer responses are returned from the scaffold. In this story, there should be no GeoServer network calls at all.

### Docker Requirements

- Docker is part of the product target, not just a dev convenience.
- Use a pinned Python 3.13 base image, preferably a slim image such as `python:3.13.x-slim` or an explicitly pinned digest if practical.
- Docker's Python guide recommends choosing a Python base image, creating Docker assets, using `.dockerignore`, and running as a non-privileged user. Source: https://docs.docker.com/guides/python/containerize/
- Docker build best practices say to use `USER` for services that do not need privileges and prefer explicit UID/GID. Source: https://docs.docker.com/build/building/best-practices/
- Runtime should start with no GeoServer config and no mounted Data Directory.
- Do not normalize real or default GeoServer production credentials in examples.

### Dependency Guidance

- Required runtime dependency for this story: `mcp`.
- Development dependencies for this story: `pytest`, `ruff`.
- Do not add `httpx`, `pydantic`, `pydantic-settings`, `respx`, XML parsers, or Docker GeoServer fixtures unless they are required by the minimal scaffold. Those belong to later stories unless needed for server construction.
- Architecture references current package checks for `httpx` 0.28.1 and Pydantic v2/pydantic-settings for later stories; do not introduce them prematurely.

### File Structure Requirements

Expected new or updated files:

```text
README.md
pyproject.toml
uv.lock
.python-version
.dockerignore
Dockerfile
docker-compose.yml
.github/workflows/ci.yml
src/geoserver_mcp/
  __init__.py
  __main__.py
  server.py
  config/__init__.py
  domain/__init__.py
  services/__init__.py
  adapters/__init__.py
  adapters/mcp/__init__.py
  adapters/geoserver_rest/__init__.py
  adapters/ogc/__init__.py
  adapters/data_directory/__init__.py
  diagnostics/__init__.py
  reporting/__init__.py
  security/__init__.py
  observability/__init__.py
tests/unit/test_scaffold.py
```

Existing files to preserve:

- `.agents/`
- `_bmad/`
- `_bmad-output/`
- `.gitignore`
- `docs/`

There are no existing application source files to update in this story.

### Testing Requirements

- Smoke tests must run with `uv run pytest`.
- Ruff checks must be documented and should run in CI.
- Docker image build must be part of the local or CI quality gate.
- Tests must not require a live GeoServer instance.
- Tests must not require local Data Directory access.
- Tests should prove the package imports and the MCP app/server factory can be constructed without config.

### Git / Previous Story Context

- This is the first implementation story. There is no previous story file or prior implementation pattern to preserve.
- Current git history has one planning commit: `1ff5f4f Initial BMAD planning artifacts`.
- The sprint status file was created before this story and should be updated by this workflow only for planning state. Do not mark the story `in-progress` or `done` until development actually starts/completes.

### Anti-Patterns To Avoid

- Do not create a single-file prototype outside `src/geoserver_mcp/`.
- Do not put MCP SDK imports in domain, services, diagnostics, reporting, or security modules.
- Do not create a FastAPI web app, REST API, dashboard, or frontend.
- Do not add GeoServer REST calls in Story 1.1.
- Do not add `check_instances` yet.
- Do not bake secrets, credentials, `.env` files, mounted data, or local runtime logs into the image or repository.
- Do not remove or reorganize BMAD artifacts.

## Project Structure Notes

The current repository contains BMAD installation files and planning artifacts only. This story creates the first application source tree. The implementation should make the repo usable as both:

- a Python package project driven by `uv`, and
- a Dockerized MCP server runtime stub.

The story intentionally stops at scaffold/runtime readiness. Later stories add configuration, safe GeoServer HTTP access, `check_instances`, read-only boundary tests, and GeoServer fixture containers.

## References

- [Source: epics.md Story 1.1](../planning-artifacts/epics.md)
- [Source: architecture.md Starter Template Evaluation and Project Structure](../planning-artifacts/architecture.md)
- [Source: prd.md FR-1, FR-17, FR-18, FR-19](../planning-artifacts/prds/prd-geoserver-mcp-2026-05-25/prd.md)
- [uv project initialization](https://docs.astral.sh/uv/concepts/projects/init/)
- [Python 3.13 documentation](https://docs.python.org/3.13/)
- [Official MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [mcp on PyPI](https://pypi.org/project/mcp/)
- [Docker Python containerization guide](https://docs.docker.com/guides/python/containerize/)
- [Docker build best practices](https://docs.docker.com/build/building/best-practices/)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- 2026-05-31: `uv` was not available on PATH, so it was installed into the workspace `.venv` instead of globally.
- 2026-05-31: Initial red test run produced 1 passed and 2 failed tests because `geoserver_mcp.server` and `geoserver_mcp.__main__` did not exist yet.
- 2026-05-31: `uv run pytest` passed with 3 scaffold smoke tests.
- 2026-05-31: Initial Ruff run scanned BMAD-installed skill files; Ruff was scoped to project source/tests by excluding `.agents`, `_bmad`, and `_bmad-output`.
- 2026-05-31: `uv run ruff check --no-cache .` and `uv run ruff format --check --no-cache .` passed.
- 2026-05-31: `docker --config .\.docker-config build --tag geoserver-mcp:dev .` passed.
- 2026-05-31: Container smoke checks passed: entrypoint reported `geoserver-mcp 0.1.0`, effective UID/GID was `10001:10001`, and the default Streamable HTTP process reached Uvicorn startup.
- 2026-06-21: Code review patches passed `uv` pytest, Ruff lint, Ruff format check, Docker build, Docker entrypoint smoke, Docker startup smoke, CLI env validation checks, and setup-uv tag resolution.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Implemented a `uv`-managed Python 3.13 package scaffold with `src/geoserver_mcp/` layout and `geoserver-mcp` console entrypoint.
- Added a minimal FastMCP app factory that constructs without GeoServer configuration and performs no GeoServer network access.
- Added architecture package boundaries for config, domain, services, adapters, diagnostics, reporting, security, and observability.
- Added smoke tests for package import, app construction, and entrypoint wiring.
- Added Docker runtime scaffold using `python:3.13.5-slim-bookworm`, explicit non-root UID/GID, Streamable HTTP defaults, and Docker Compose.
- Added CI quality gate that runs uv sync, pytest, Ruff lint, Ruff format check, and Docker build.

### File List

- .dockerignore
- .github/workflows/ci.yml
- .gitignore
- .python-version
- Dockerfile
- README.md
- docker-compose.yml
- pyproject.toml
- uv.lock
- src/geoserver_mcp/__init__.py
- src/geoserver_mcp/__main__.py
- src/geoserver_mcp/server.py
- src/geoserver_mcp/adapters/__init__.py
- src/geoserver_mcp/adapters/data_directory/__init__.py
- src/geoserver_mcp/adapters/geoserver_rest/__init__.py
- src/geoserver_mcp/adapters/mcp/__init__.py
- src/geoserver_mcp/adapters/mcp/server.py
- src/geoserver_mcp/adapters/ogc/__init__.py
- src/geoserver_mcp/config/__init__.py
- src/geoserver_mcp/diagnostics/__init__.py
- src/geoserver_mcp/domain/__init__.py
- src/geoserver_mcp/observability/__init__.py
- src/geoserver_mcp/reporting/__init__.py
- src/geoserver_mcp/security/__init__.py
- src/geoserver_mcp/services/__init__.py
- tests/unit/test_scaffold.py
- _bmad-output/implementation-artifacts/1-1-initialize-dockerized-python-mcp-server-scaffold.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

### Change Log

- 2026-05-31: Implemented Story 1.1 scaffold and moved story to review.
- 2026-06-21: Addressed code review findings and moved story to done.
