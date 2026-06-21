# Story 2.1: List Configured Instance Inventory Summary

Status: done

## Story

As a GeoServer administrator,
I want to list all configured GeoServer instances with inspection status,
so that I can see which instances are available for catalog inventory.

## Acceptance Criteria

1. Given the MCP server has multiple configured instances, when an MCP client requests the instance inventory summary, then the response includes each instance ID, base URL, reachability status, inspected surfaces, and unavailable information, and secret values are redacted.
2. Given an instance cannot be reached or authenticated, when the instance summary is generated, then the response includes a reason code for that instance and other instances are still reported.

## Tasks / Subtasks

- [x] Add instance inventory summary models. (AC: 1, 2)
  - [x] Add a catalog/inventory domain model for configured instance summaries.
  - [x] Include instance ID, base URL, reachable/authenticated flags, inspected surfaces, unavailable information, and optional reason code.
- [x] Implement instance summary inventory service. (AC: 1, 2)
  - [x] Reuse Story 1.4 `check_instances` orchestration instead of duplicating GeoServer calls.
  - [x] Preserve one-result-per-instance behavior for mixed success/failure.
  - [x] Keep output redacted and structured with the shared response envelope.
- [x] Expose the first `list_catalog` MCP tool slice. (AC: 1, 2)
  - [x] Register `list_catalog` under the MCP adapter boundary when runtime config is supplied.
  - [x] Support `resource_types=["instances"]` and default to instance summaries when no resource types are supplied.
  - [x] Do not implement workspaces, stores, layers, styles, or resource detail yet.
- [x] Add focused tests. (AC: 1, 2)
  - [x] Add service tests for all-success and mixed success/failure instance summaries.
  - [x] Add MCP registration/call tests for `list_catalog` instance summaries.
  - [x] Add redaction assertions.
  - [x] Preserve existing `check_instances` tests.
- [x] Run and document the quality gate. (AC: all)
  - [x] Run `.\.venv\Scripts\uv.exe run ruff format --check .`.
  - [x] Run `.\.venv\Scripts\uv.exe run ruff check .`.
  - [x] Run `.\.venv\Scripts\uv.exe run pytest`.
  - [x] Run `git diff --check`.
  - [x] Run Docker build if packaged source changed.
  - [x] Update this story's Dev Agent Record, File List, and Change Log only after checks pass.

### Review Findings

- [x] [Review][Patch] Unsupported `list_catalog` resource types are untested [tests/unit/test_mcp_list_catalog.py:38]
- [x] [Review][Patch] `list_instance_inventory` lacks the default GeoServer client factory used by adjacent services [src/geoserver_mcp/services/inventory_service.py:14]

## Dev Notes

### Source Context

- Story source: `_bmad-output/planning-artifacts/epics.md` Story 2.1.
- Architecture source: `_bmad-output/planning-artifacts/architecture.md` API naming conventions, response formats, and service boundaries.
- Previous story source: `_bmad-output/implementation-artifacts/1-6-add-initial-docker-compose-geoserver-fixture.md`.

### Architecture Requirements

- Public tool name must be `list_catalog`; do not add a separate `list_instances` tool.
- Business orchestration belongs under `src/geoserver_mcp/services/`.
- MCP SDK imports stay under `src/geoserver_mcp/adapters/mcp/`.
- Reuse `check_instances` for connectivity evidence.
- Keep top-level response shape `status`, `data`, `findings`, `errors`, and `metadata`.

### Implementation Guidance

- This story implements only `resource_types=["instances"]`.
- Later Epic 2 stories should extend the same `list_catalog` tool/service rather than creating one tool per resource type.
- Use inspected surface value `geoserver_rest:about_version` for successful connectivity/version checks.
- For unavailable information, carry reason code and message from the failed instance status.

### Anti-Patterns To Avoid

- Do not add catalog REST endpoint calls for workspaces/stores/layers/styles yet.
- Do not add raw GeoServer endpoint proxying.
- Do not fail the whole summary because one instance is unavailable.
- Do not expose secrets.

## Project Structure Notes

Story 2.1 starts the catalog inventory surface with configured instance summaries only. It should preserve all Epic 1 behavior and prepare for later `list_catalog` expansion.

## References

- [Source: epics.md Story 2.1](../planning-artifacts/epics.md)
- [Source: architecture.md API Naming and Response Formats](../planning-artifacts/architecture.md)
- [Previous story: Story 1.6 GeoServer fixture](1-6-add-initial-docker-compose-geoserver-fixture.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- 2026-06-21: Created Story 2.1 and marked it ready for development.
- 2026-06-21: Started Story 2.1 implementation.
- 2026-06-21: Confirmed red phase with `.\.venv\Scripts\uv.exe run pytest tests\unit\test_inventory_service.py tests\unit\test_mcp_list_catalog.py` failing on missing `inventory_service`.
- 2026-06-21: `.\.venv\Scripts\uv.exe run pytest tests\unit\test_inventory_service.py tests\unit\test_mcp_list_catalog.py tests\unit\test_read_only_safety.py` passed with 6 tests.
- 2026-06-21: `.\.venv\Scripts\uv.exe run ruff format --check .` passed.
- 2026-06-21: `.\.venv\Scripts\uv.exe run ruff check .` passed.
- 2026-06-21: `.\.venv\Scripts\uv.exe run pytest` passed with 60 tests, 1 skipped gated fixture integration test, and the existing pytest cache access warning.
- 2026-06-21: `git diff --check` passed with LF-to-CRLF warnings only.
- 2026-06-21: `docker build -t geoserver-mcp:story-2-1 .` passed.
- 2026-06-21: BMAD code review completed with 0 decision-needed, 2 patch, 0 deferred findings.
- 2026-06-21: Applied review patches for unsupported resource-type coverage and default inventory client factory.
- 2026-06-21: `.\.venv\Scripts\uv.exe run pytest tests\unit\test_inventory_service.py tests\unit\test_mcp_list_catalog.py` passed with 4 tests.
- 2026-06-21: `.\.venv\Scripts\uv.exe run ruff format --check .` passed.
- 2026-06-21: `.\.venv\Scripts\uv.exe run ruff check .` passed.
- 2026-06-21: `.\.venv\Scripts\uv.exe run pytest` passed with 61 tests, 1 skipped gated fixture integration test, and the existing pytest cache access warning.
- 2026-06-21: `git diff --check` passed with LF-to-CRLF warnings only.
- 2026-06-21: `docker build -t geoserver-mcp:story-2-1-review .` passed.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added `InstanceInventorySummary` domain model.
- Added instance inventory service that reuses `check_instances` and returns configured instance summaries.
- Added `list_catalog` MCP tool registration for the initial `instances` resource type.
- Added service and MCP tests for instance summaries, mixed success/failure, redaction, and read-only guardrail compatibility.
- Resolved all Story 2.1 code review findings and moved the story to done.

### File List

- _bmad-output/implementation-artifacts/2-1-list-configured-instance-inventory-summary.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- src/geoserver_mcp/adapters/mcp/server.py
- src/geoserver_mcp/adapters/mcp/tools.py
- src/geoserver_mcp/domain/__init__.py
- src/geoserver_mcp/domain/catalog.py
- src/geoserver_mcp/services/__init__.py
- src/geoserver_mcp/services/inventory_service.py
- tests/unit/test_inventory_service.py
- tests/unit/test_mcp_list_catalog.py

### Change Log

- 2026-06-21: Created Story 2.1 and marked it ready for development.
- 2026-06-21: Moved Story 2.1 to in-progress.
- 2026-06-21: Implemented instance summary inventory via `list_catalog`, tests, and quality gates; moved story to review.
- 2026-06-21: Applied code review patches, reran quality gates, and marked Story 2.1 done.
