# Story 1.5: Enforce Read-Only MCP Safety Boundary

Status: done

## Story

As a GeoServer administrator,
I want v1 MCP tools to be read-only by construction,
so that connecting the MCP server to admin-level GeoServer credentials cannot mutate deployments.

## Acceptance Criteria

1. Given the MCP server registers its v1 tools, when the tool list is inspected, then no create, update, delete, reload, purge, or mutation tool is exposed.
2. Given a developer adds GeoServer REST adapter methods, when unit tests inspect the adapter contract, then v1 adapter methods are limited to GET/read-only operations.
3. Given a user asks for a mutation capability through the MCP server, when no v1 mutation tool exists, then the server does not perform any GeoServer mutation and guided responses or prompts identify mutation as unsupported in v1.

## Tasks / Subtasks

- [x] Add read-only safety definitions. (AC: 1, 2, 3)
  - [x] Add a central list of mutation verbs/terms under `src/geoserver_mcp/security/` or an MCP safety module.
  - [x] Add helper checks for public MCP tool names and GeoServer REST client methods.
  - [x] Add a stable v1 unsupported-mutation guidance string.
- [x] Enforce MCP tool registration safety. (AC: 1, 3)
  - [x] Add tests that inspect FastMCP tool names and fail if create/update/delete/reload/purge/mutation tools are exposed.
  - [x] Keep `check_instances` registered as the only current tool when runtime config is supplied.
  - [x] Add a read-only safety prompt or guidance surface that tells agents mutation/admin-write actions are unsupported in v1.
- [x] Enforce GeoServer REST adapter safety. (AC: 2)
  - [x] Add tests that inspect `GeoServerRestClient` public callable methods and fail if write-like methods are added.
  - [x] Add tests proving HTTPX request execution still goes through GET-only methods for the current adapter.
  - [x] Do not add write-capable helper methods or generic request methods.
- [x] Preserve existing behavior. (AC: all)
  - [x] Keep `create_mcp_app()` usable without config.
  - [x] Keep `check_instances` behavior and Story 1.3 REST client behavior green.
  - [x] Do not implement any mutation endpoint or mutation response tool.
- [x] Run and document the quality gate. (AC: all)
  - [x] Run `.\.venv\Scripts\uv.exe run ruff format --check .`.
  - [x] Run `.\.venv\Scripts\uv.exe run ruff check .`.
  - [x] Run `.\.venv\Scripts\uv.exe run pytest`.
  - [x] Run `git diff --check`.
  - [x] Run Docker build if packaged source changed.
  - [x] Update this story's Dev Agent Record, File List, and Change Log only after checks pass.

### Review Findings

- [x] [Review][Patch] Read-only guardrail tests are too exact and would block future read-only tools or REST methods [tests/unit/test_read_only_safety.py:46]

## Dev Notes

### Source Context

- Story source: `_bmad-output/planning-artifacts/epics.md` Story 1.5.
- Architecture source: `_bmad-output/planning-artifacts/architecture.md` API naming conventions, enforcement guidelines, anti-pattern examples, and read-only safety rules.
- Previous story source: `_bmad-output/implementation-artifacts/1-4-expose-check-instances-mcp-tool.md`.

### Architecture Requirements

- v1 must not expose create, update, delete, reload, purge, or other mutation tools.
- MCP tool names must be task-level and read-only.
- GeoServer REST access must remain GET-only.
- Do not add raw endpoint proxy tools or generic request methods.
- MCP SDK imports stay under `src/geoserver_mcp/adapters/mcp/`.
- The safety guidance surface must not perform any GeoServer call.

### Current Code To Preserve

- `check_instances` is the only current MCP tool and is read-only.
- `GeoServerRestClient` currently exposes `get_connectivity_metadata()` and `get_json()` only for HTTP access.
- Story 1.4 preserved config-free app construction; this must remain true.

### Implementation Guidance

- Use tests as the enforcement mechanism. This story is primarily about guardrails, not new operational capability.
- Prefer a small prompt named `read_only_safety` or similar over adding a mutation tool.
- The prompt should explicitly state that v1 does not support create, update, delete, reload, purge, or other GeoServer mutation actions.

### Anti-Patterns To Avoid

- Do not add a `mutate`, `admin`, `request`, `proxy`, `reload`, `purge`, or `delete` tool.
- Do not add POST/PUT/PATCH/DELETE methods to the REST adapter.
- Do not implement catalog inventory, Docker fixture work, diagnostics, or prompt workflows beyond read-only safety guidance.

## Project Structure Notes

Story 1.5 should be a narrow safety-boundary hardening story. The main output is automated enforcement that prevents future stories from accidentally exposing mutation surfaces.

## References

- [Source: epics.md Story 1.5](../planning-artifacts/epics.md)
- [Source: architecture.md Safety and Anti-Patterns](../planning-artifacts/architecture.md)
- [Previous story: Story 1.4 check_instances MCP tool](1-4-expose-check-instances-mcp-tool.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- 2026-06-21: Created Story 1.5 and marked it ready for development.
- 2026-06-21: Started Story 1.5 implementation.
- 2026-06-21: Confirmed red phase with `.\.venv\Scripts\uv.exe run pytest tests\unit\test_read_only_safety.py` failing on missing `geoserver_mcp.security.read_only`.
- 2026-06-21: `.\.venv\Scripts\uv.exe run pytest tests\unit\test_read_only_safety.py` passed with 3 tests.
- 2026-06-21: `.\.venv\Scripts\uv.exe run ruff format --check .` passed.
- 2026-06-21: `.\.venv\Scripts\uv.exe run ruff check .` passed.
- 2026-06-21: `.\.venv\Scripts\uv.exe run pytest` passed with 57 tests and the existing pytest cache access warning.
- 2026-06-21: `git diff --check` passed with LF-to-CRLF warnings only.
- 2026-06-21: `docker build -t geoserver-mcp:story-1-5 .` passed.
- 2026-06-21: BMAD code review completed with 0 decision-needed, 1 patch, 0 deferred findings.
- 2026-06-21: Applied review patch to keep read-only guardrail tests compatible with future read-only tools and REST methods.
- 2026-06-21: `.\.venv\Scripts\uv.exe run pytest tests\unit\test_read_only_safety.py` passed with 3 tests.
- 2026-06-21: `.\.venv\Scripts\uv.exe run ruff format --check .` passed.
- 2026-06-21: `.\.venv\Scripts\uv.exe run ruff check .` passed.
- 2026-06-21: `.\.venv\Scripts\uv.exe run pytest` passed with 57 tests and the existing pytest cache access warning.
- 2026-06-21: `git diff --check` passed with LF-to-CRLF warnings only.
- 2026-06-21: `docker build -t geoserver-mcp:story-1-5-review .` passed.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added central read-only safety terms and unsupported mutation guidance.
- Added read-only safety MCP prompt registration under the MCP adapter boundary.
- Added tests enforcing current MCP tools and GeoServer REST public methods stay read-only.
- Preserved config-free app creation and existing `check_instances` behavior.
- Resolved the Story 1.5 code review finding and moved the story to done.

### File List

- _bmad-output/implementation-artifacts/1-5-enforce-read-only-mcp-safety-boundary.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- src/geoserver_mcp/adapters/mcp/prompts.py
- src/geoserver_mcp/adapters/mcp/server.py
- src/geoserver_mcp/security/__init__.py
- src/geoserver_mcp/security/read_only.py
- tests/unit/test_read_only_safety.py

### Change Log

- 2026-06-21: Created Story 1.5 and marked it ready for development.
- 2026-06-21: Moved Story 1.5 to in-progress.
- 2026-06-21: Implemented read-only MCP safety guardrails, prompt guidance, tests, and quality gates; moved story to review.
- 2026-06-21: Applied code review patch, reran quality gates, and marked Story 1.5 done.
