# Story 2.2: List Workspaces Across Instances

Status: done

## Story

As a GeoServer administrator,
I want to list workspaces for one or more GeoServer instances,
so that I can understand the top-level catalog organization.

## Acceptance Criteria

1. Given a reachable authenticated GeoServer instance, when an MCP client requests workspace inventory, then the response includes workspace names and owning instance IDs, and each workspace includes identifiers needed for follow-up store/layer inspection.
2. Given multiple instances are requested, when one instance fails, then successful workspace results are still returned for other instances, and the failed instance is represented with a reason code.

## Tasks / Subtasks

- [x] Add workspace inventory domain model. (AC: 1)
  - [x] Add a structured workspace item with instance ID, workspace name, resource ID, and optional REST href.
  - [x] Export the model from the shared domain boundary.
- [x] Extend safe GeoServer REST access. (AC: 1, 2)
  - [x] Add a read-only `list_workspaces` helper that calls `rest/workspaces.json`.
  - [x] Keep the call inside the existing safe GET-only client path.
- [x] Implement workspace inventory service. (AC: 1, 2)
  - [x] Fetch workspaces per configured instance.
  - [x] Preserve successful workspace results when another instance fails.
  - [x] Map malformed workspace payloads and failed instance calls to structured reason-code errors.
  - [x] Redact secrets from workspace names, hrefs, errors, and serialized output.
- [x] Extend `list_catalog` MCP routing. (AC: 1, 2)
  - [x] Support `resource_types=["workspaces"]`.
  - [x] Preserve default `resource_types=["instances"]` behavior.
  - [x] Keep mixed resource-type requests unsupported until request-scoped caching is implemented.
- [x] Update documentation. (AC: 1)
  - [x] Update README tool capability text for `check_instances` and `list_catalog`.
- [x] Run and document the quality gate. (AC: all)
  - [x] Run focused unit tests for REST client, inventory service, MCP `list_catalog`, and read-only guardrails.
  - [x] Run full pytest, Ruff lint, Ruff format check, and `git diff --check`.

### Review Findings

- None in this implementation pass.

## Dev Notes

### Source Context

- Story source: `_bmad-output/planning-artifacts/epics.md` Story 2.2.
- Previous story source: `_bmad-output/implementation-artifacts/2-1-list-configured-instance-inventory-summary.md`.

### Architecture Requirements

- Continue extending `list_catalog`; do not add a separate `list_workspaces` MCP tool.
- Business orchestration belongs under `src/geoserver_mcp/services/`.
- MCP SDK imports stay under `src/geoserver_mcp/adapters/mcp/`.
- GeoServer REST calls stay behind the safe GET-only adapter.
- Keep the shared top-level response shape: `status`, `data`, `findings`, `errors`, and `metadata`.
- Do not expose secrets or mutation operations.

### Implementation Guidance

- Use GeoServer REST workspace inventory endpoint `rest/workspaces.json`.
- Normalize the common GeoServer shape `{"workspaces": {"workspace": [...]}}`.
- Treat malformed successful responses as `parse_error`.
- Return `partial` when at least one instance succeeds and at least one instance fails.

### Anti-Patterns To Avoid

- Do not add raw endpoint proxying.
- Do not fail the entire workspace inventory request because one instance fails.
- Do not add store, layer, style, detail, OGC, diagnostics, or cache behavior in this story.

## Project Structure Notes

Story 2.2 expands the existing catalog inventory surface from configured instance summaries to GeoServer workspaces. It prepares follow-up Epic 2 stories for stores, layers, styles, resource detail, and request-scoped caching.

## References

- [Source: epics.md Story 2.2](../planning-artifacts/epics.md)
- [Previous story: Story 2.1 instance summaries](2-1-list-configured-instance-inventory-summary.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- 2026-06-22: Implemented workspace inventory domain model, REST client helper, service aggregation, MCP routing, and README tool documentation.
- 2026-06-22: `.\.venv\Scripts\uv.exe run pytest tests\unit\test_geoserver_rest_client.py tests\unit\test_inventory_service.py tests\unit\test_mcp_list_catalog.py tests\unit\test_read_only_safety.py` initially failed because `uv` tried to use the user-level cache outside the workspace.
- 2026-06-22: Reran focused tests with `UV_CACHE_DIR=.uv-cache`; 28 tests passed.

### Completion Notes List

- Added `WorkspaceInventoryItem` domain model.
- Added `GeoServerRestClient.list_workspaces()` through the existing safe GET-only request path.
- Added workspace inventory service that returns normalized workspace items and per-instance reason-code errors.
- Extended `list_catalog` to support `resource_types=["workspaces"]`.
- Updated README MCP tool documentation.

### File List

- README.md
- _bmad-output/implementation-artifacts/2-2-list-workspaces-across-instances.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- src/geoserver_mcp/adapters/geoserver_rest/client.py
- src/geoserver_mcp/adapters/mcp/tools.py
- src/geoserver_mcp/domain/__init__.py
- src/geoserver_mcp/domain/catalog.py
- src/geoserver_mcp/services/__init__.py
- src/geoserver_mcp/services/inventory_service.py
- tests/unit/test_geoserver_rest_client.py
- tests/unit/test_inventory_service.py
- tests/unit/test_mcp_list_catalog.py

### Change Log

- 2026-06-22: Created, implemented, tested, and marked Story 2.2 done.
