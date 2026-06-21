# Story 1.4: Expose `check_instances` MCP Tool

Status: done

## Story

As a GeoServer administrator,
I want an AI agent to check all configured GeoServer instances,
so that I can quickly understand which instances are reachable, authenticated, and inspectable.

## Acceptance Criteria

1. Given the MCP server is running with multiple configured instances, when an MCP client invokes `check_instances`, then the response includes one status result per configured instance and one failed instance does not prevent results for other instances.
2. Given an instance is reachable and authenticated, when `check_instances` runs, then the result includes reachability status and basic server metadata when available.
3. Given an instance fails due to network, auth, forbidden, unsupported endpoint, or unexpected response, when `check_instances` runs, then the result includes a structured reason code and human-readable explanation and secrets are redacted from all output.

## Tasks / Subtasks

- [x] Add shared response and instance status models. (AC: 1, 2, 3)
  - [x] Add top-level response primitives under `src/geoserver_mcp/domain/` with `status`, `data`, `findings`, `errors`, and `metadata`.
  - [x] Add an instance connectivity/status model with instance ID, reachable/authenticated booleans, optional version metadata, reason code, message, HTTP status, and evidence URL.
  - [x] Ensure model serialization uses JSON-safe enum values and redacted strings.
- [x] Implement check-instance orchestration under `src/geoserver_mcp/services/`. (AC: 1, 2, 3)
  - [x] Add a service function that accepts `RuntimeConfig`, calls the Story 1.3 GeoServer REST client once per instance, and returns one status result per configured instance.
  - [x] Ensure one failed instance does not stop other instances from being checked.
  - [x] Map successful Story 1.3 responses to reachable/authenticated status and extract basic GeoServer version metadata when available.
  - [x] Map failed Story 1.3 responses to structured per-instance errors with `ReasonCode`.
  - [x] Redact all serialized output.
- [x] Register `check_instances` under the MCP adapter boundary. (AC: 1, 2, 3)
  - [x] Keep all MCP SDK imports under `src/geoserver_mcp/adapters/mcp/`.
  - [x] Add a registration helper that binds `check_instances` to a provided `RuntimeConfig`.
  - [x] Keep `create_mcp_app()` usable without config and without registering the tool, preserving Story 1.1 smoke behavior.
  - [x] Allow `create_mcp_app(..., runtime_config=...)` and `create_app(..., runtime_config=...)` to register the tool for tests and later CLI wiring.
- [x] Add focused tests. (AC: 1, 2, 3)
  - [x] Add service tests proving mixed success/failure returns all instances and top-level `partial`.
  - [x] Add tests for success metadata extraction, auth/forbidden/network/unsupported/unknown reason codes, and redaction.
  - [x] Add MCP registration tests proving `check_instances` is discoverable when runtime config is supplied and absent when no config is supplied.
  - [x] Keep tests local and mocked; do not require a live GeoServer container.
- [x] Preserve Story 1.1 through 1.3 boundaries. (AC: all)
  - [x] Do not add mutation tools, generic endpoint proxying, catalog inventory, OGC parsing, Data Directory reads, or Docker fixtures in this story.
  - [x] Do not move MCP app creation out of `adapters/mcp/`.
  - [x] Do not make startup require a config file.
- [x] Run and document the quality gate. (AC: all)
  - [x] Run `.\.venv\Scripts\uv.exe run ruff format --check .`.
  - [x] Run `.\.venv\Scripts\uv.exe run ruff check .`.
  - [x] Run `.\.venv\Scripts\uv.exe run pytest`.
  - [x] Run `git diff --check`.
  - [x] Run Docker build if packaged source changed.
  - [x] Update this story's Dev Agent Record, File List, and Change Log only after checks pass.

### Review Findings

- [x] [Review][Patch] Unexpected client factory or client call exceptions can still abort the whole `check_instances` response [src/geoserver_mcp/services/instance_service.py:31]

## Dev Notes

### Source Context

- Story source: `_bmad-output/planning-artifacts/epics.md` Story 1.4.
- Architecture source: `_bmad-output/planning-artifacts/architecture.md` API naming conventions, response shape, error handling, and MCP boundary rules.
- Previous story source: `_bmad-output/implementation-artifacts/1-3-implement-safe-geoserver-http-client-for-read-only-access.md`.

### Architecture Requirements

- Public tool name must be `check_instances`.
- Use the shared top-level response shape: `status`, `data`, `findings`, `errors`, and `metadata`.
- MCP SDK imports stay under `src/geoserver_mcp/adapters/mcp/`.
- Business orchestration belongs under `src/geoserver_mcp/services/`.
- GeoServer HTTP calls must continue to flow through `src/geoserver_mcp/adapters/geoserver_rest/`.
- One instance failure must produce a per-instance failed status and must not prevent other instance results.
- User-visible output must not include usernames, passwords, raw adapter exceptions, or unredacted credential-bearing values.

### Current Code To Preserve

- Story 1.2 config loading and `RuntimeConfig` resolution already provide redaction-safe runtime instance configs.
- Story 1.3 `GeoServerRestClient.get_connectivity_metadata()` returns a structured `GeoServerRestResult`; reuse it rather than issuing HTTP directly from the service or MCP adapter.
- `create_mcp_app()` currently works without configuration; keep that behavior.

### Implementation Guidance

- Keep version extraction conservative. GeoServer version metadata may appear in `about.resource[]` entries using keys such as `Version` or `version`; if unavailable, return `None` with a successful reachable/authenticated status.
- Set top-level status to `success` when all instances succeed, `partial` when at least one succeeds and at least one fails, and `failed` when all configured instances fail.
- Include operation metadata such as tool name and instance IDs. Do not include secret values.
- In MCP registration tests, use FastMCP `list_tools()` and `call_tool()` directly rather than starting a server process.

### Anti-Patterns To Avoid

- Do not register one MCP tool per GeoServer endpoint.
- Do not add write/mutation tools.
- Do not let MCP adapter code reach around the service layer into `httpx`.
- Do not fail the whole response because one instance fails.
- Do not require Docker or a live GeoServer for unit tests.

## Project Structure Notes

Story 1.4 should create the first vertical slice from runtime config through service orchestration to MCP registration. It must stay narrow: connectivity status only, not catalog inventory or Docker fixture integration.

## References

- [Source: epics.md Story 1.4](../planning-artifacts/epics.md)
- [Source: architecture.md API Naming, Response Formats, Boundaries](../planning-artifacts/architecture.md)
- [Previous story: Story 1.3 safe GeoServer REST client](1-3-implement-safe-geoserver-http-client-for-read-only-access.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- 2026-06-21: Created Story 1.4 and marked it ready for development.
- 2026-06-21: Started Story 1.4 implementation.
- 2026-06-21: Confirmed red phase with `.\.venv\Scripts\uv.exe run pytest tests\unit\test_instance_service.py tests\unit\test_mcp_check_instances.py` failing on missing `ResponseStatus`.
- 2026-06-21: `.\.venv\Scripts\uv.exe run pytest tests\unit\test_instance_service.py tests\unit\test_mcp_check_instances.py` passed with 9 tests.
- 2026-06-21: `.\.venv\Scripts\uv.exe run ruff format --check .` passed.
- 2026-06-21: `.\.venv\Scripts\uv.exe run ruff check .` passed.
- 2026-06-21: `.\.venv\Scripts\uv.exe run pytest` passed with 53 tests and the existing pytest cache access warning.
- 2026-06-21: `.\.venv\Scripts\uv.exe run geoserver-mcp --version` returned `geoserver-mcp 0.1.0`.
- 2026-06-21: MCP app construction smoke check returned `FastMCP`.
- 2026-06-21: `git diff --check` passed with LF-to-CRLF warnings only.
- 2026-06-21: `docker build -t geoserver-mcp:story-1-4 .` passed.
- 2026-06-21: BMAD code review completed with 0 decision-needed, 1 patch, 0 deferred findings.
- 2026-06-21: Applied review patch to isolate unexpected client factory/client call exceptions per instance.
- 2026-06-21: `.\.venv\Scripts\uv.exe run pytest tests\unit\test_instance_service.py tests\unit\test_mcp_check_instances.py` passed with 10 tests.
- 2026-06-21: `.\.venv\Scripts\uv.exe run ruff format --check .` passed.
- 2026-06-21: `.\.venv\Scripts\uv.exe run ruff check .` passed.
- 2026-06-21: `.\.venv\Scripts\uv.exe run pytest` passed with 54 tests and the existing pytest cache access warning.
- 2026-06-21: `git diff --check` passed with LF-to-CRLF warnings only.
- 2026-06-21: `docker build -t geoserver-mcp:story-1-4-review .` passed.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added shared response primitives and instance connectivity status models.
- Added `check_instances` service orchestration that isolates per-instance failures and returns `success`, `partial`, or `failed`.
- Added MCP registration for `check_instances` when runtime config is provided while preserving config-free app creation.
- Added service and MCP registration tests for mixed results, reason-code propagation, redaction, and tool discovery/callability.
- Resolved the Story 1.4 code review finding and moved the story to done.

### File List

- _bmad-output/implementation-artifacts/1-4-expose-check-instances-mcp-tool.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- src/geoserver_mcp/adapters/mcp/server.py
- src/geoserver_mcp/adapters/mcp/tools.py
- src/geoserver_mcp/domain/__init__.py
- src/geoserver_mcp/domain/enums.py
- src/geoserver_mcp/domain/responses.py
- src/geoserver_mcp/server.py
- src/geoserver_mcp/services/__init__.py
- src/geoserver_mcp/services/instance_service.py
- tests/unit/test_instance_service.py
- tests/unit/test_mcp_check_instances.py

### Change Log

- 2026-06-21: Created Story 1.4 and marked it ready for development.
- 2026-06-21: Moved Story 1.4 to in-progress.
- 2026-06-21: Implemented `check_instances` service and MCP registration with tests and quality gates; moved story to review.
- 2026-06-21: Applied code review patch, reran quality gates, and marked Story 1.4 done.
