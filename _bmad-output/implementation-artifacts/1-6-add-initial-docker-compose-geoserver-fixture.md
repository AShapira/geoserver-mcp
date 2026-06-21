# Story 1.6: Add Initial Docker Compose GeoServer Fixture

Status: done

## Story

As a GeoServer MCP maintainer,
I want a local Docker Compose fixture with GeoServer,
so that the connectivity flow can be tested against a real GeoServer container.

## Acceptance Criteria

1. Given the repository includes Docker Compose fixture configuration, when the fixture stack starts, then at least one GeoServer container is reachable from the MCP server container or local test process.
2. Given test credentials are configured for the fixture, when integration tests run against the fixture, then `check_instances` can report a successful reachable/authenticated instance.
3. Given the fixture uses test credentials, when examples and docs reference them, then they are clearly marked as local-test-only and production examples do not normalize default GeoServer credentials.

## Tasks / Subtasks

- [x] Add Docker Compose GeoServer fixture configuration. (AC: 1)
  - [x] Add a pinned GeoServer container image to `docker-compose.yml`.
  - [x] Put the GeoServer fixture behind a Compose profile so normal MCP-only startup remains unchanged.
  - [x] Expose GeoServer on localhost for local integration tests and make it reachable to the MCP container by service name.
- [x] Add local-test-only fixture examples. (AC: 2, 3)
  - [x] Add fixture config/env examples that point at the Compose GeoServer service and clearly mark default credentials as local-test-only.
  - [x] Keep production examples using placeholder env refs and no default GeoServer password values.
- [x] Add integration test coverage. (AC: 1, 2)
  - [x] Add a skipped-by-default integration test that uses the real `check_instances` service against the fixture URL.
  - [x] Gate the test with an explicit environment variable so normal unit test runs do not require Docker or a live GeoServer.
  - [x] Assert the result is reachable/authenticated and includes one instance status.
- [x] Update documentation. (AC: 1, 2, 3)
  - [x] Document how to start the fixture profile.
  - [x] Document how to run the integration test.
  - [x] Clearly state that fixture credentials are local-test-only and not production guidance.
- [x] Run and document the quality gate. (AC: all)
  - [x] Run `.\.venv\Scripts\uv.exe run ruff format --check .`.
  - [x] Run `.\.venv\Scripts\uv.exe run ruff check .`.
  - [x] Run `.\.venv\Scripts\uv.exe run pytest`.
  - [x] Run `git diff --check`.
  - [x] Run Docker build/Compose config validation for changed Docker assets.
  - [x] Update this story's Dev Agent Record, File List, and Change Log only after checks pass.

### Review Findings

- [x] [Review][Patch] Fixture docs/examples do not distinguish host `localhost` URL from Compose service URL for the MCP container [examples/geoserver-mcp.fixture.yaml:5]

## Dev Notes

### Source Context

- Story source: `_bmad-output/planning-artifacts/epics.md` Story 1.6.
- Architecture source: `_bmad-output/planning-artifacts/architecture.md` Infrastructure & Deployment and testing structure.
- Previous story source: `_bmad-output/implementation-artifacts/1-5-enforce-read-only-mcp-safety-boundary.md`.

### Architecture Requirements

- Docker fixture work belongs in Compose/docs/examples/tests, not in application startup logic.
- Do not make normal unit tests require Docker.
- Do not make normal `docker compose up --build` unexpectedly run a GeoServer fixture unless the fixture profile is selected.
- Keep the MCP server read-only and do not add mutation tools.

### Implementation Guidance

- Use the official GeoServer Docker image from OSGeo with a pinned tag.
- Use default `admin` / `geoserver` credentials only in files and docs marked local-test-only.
- The integration test should default to `http://localhost:8080/geoserver` for the local test process and allow override via env var.
- The MCP container can reach the fixture at `http://geoserver-fixture:8080/geoserver` when both services run in Compose.

### Anti-Patterns To Avoid

- Do not replace production examples with default GeoServer credentials.
- Do not add a fixture that always starts in normal development Compose runs.
- Do not require a live GeoServer for `uv run pytest`.
- Do not add PostGIS or sample catalog complexity in this initial fixture story.

## Project Structure Notes

This story should introduce the first real-container validation path while preserving the fast local test loop.

## References

- [Source: epics.md Story 1.6](../planning-artifacts/epics.md)
- [Source: architecture.md Infrastructure & Deployment](../planning-artifacts/architecture.md)
- [Previous story: Story 1.5 read-only safety boundary](1-5-enforce-read-only-mcp-safety-boundary.md)
- [GeoServer Docker documentation](https://docs.geoserver.org/main/en/user/installation/docker/)
- [GeoServer Docker image repository](https://github.com/geoserver/docker)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- 2026-06-21: Created Story 1.6 and marked it ready for development.
- 2026-06-21: Started Story 1.6 implementation.
- 2026-06-21: `.\.venv\Scripts\uv.exe run ruff format --check .` passed.
- 2026-06-21: `.\.venv\Scripts\uv.exe run ruff check .` passed.
- 2026-06-21: `.\.venv\Scripts\uv.exe run pytest` passed with 57 tests, 1 skipped gated fixture integration test, and the existing pytest cache access warning.
- 2026-06-21: `docker compose --profile fixture config` passed.
- 2026-06-21: `git diff --check` passed with LF-to-CRLF warnings only.
- 2026-06-21: `docker build -t geoserver-mcp:story-1-6 .` passed.
- 2026-06-21: BMAD code review completed with 0 decision-needed, 1 patch, 0 deferred findings.
- 2026-06-21: Applied review patch clarifying host-run fixture URL versus Compose service URL for MCP containers.
- 2026-06-21: `.\.venv\Scripts\uv.exe run ruff format --check .` passed.
- 2026-06-21: `.\.venv\Scripts\uv.exe run ruff check .` passed.
- 2026-06-21: `.\.venv\Scripts\uv.exe run pytest` passed with 57 tests, 1 skipped gated fixture integration test, and the existing pytest cache access warning.
- 2026-06-21: `docker compose --profile fixture config` passed.
- 2026-06-21: `git diff --check` passed with LF-to-CRLF warnings only.
- 2026-06-21: `docker build -t geoserver-mcp:story-1-6-review .` passed.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added a pinned OSGeo GeoServer fixture behind the Docker Compose `fixture` profile.
- Added local-test-only fixture config/env examples using default GeoServer credentials only in explicitly marked fixture files.
- Added a gated integration test for `check_instances` against a live local fixture.
- Updated README fixture startup and integration-test instructions.
- Resolved the Story 1.6 code review finding and moved the story to done.

### File List

- _bmad-output/implementation-artifacts/1-6-add-initial-docker-compose-geoserver-fixture.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- README.md
- docker-compose.yml
- examples/geoserver-mcp.fixture.yaml
- examples/geoserver-mcp.fixture.env.example
- tests/integration/test_check_instances_geoserver_fixture.py

### Change Log

- 2026-06-21: Created Story 1.6 and marked it ready for development.
- 2026-06-21: Moved Story 1.6 to in-progress.
- 2026-06-21: Added Docker Compose GeoServer fixture, local-test-only examples, gated integration test, docs, and quality gates; moved story to review.
- 2026-06-21: Applied code review patch, reran quality gates, and marked Story 1.6 done.
