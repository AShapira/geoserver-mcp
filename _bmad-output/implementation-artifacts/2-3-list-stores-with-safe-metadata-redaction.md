# Story 2.3: List Stores With Safe Metadata Redaction

Status: done

## Story

As a GeoServer administrator,
I want to list GeoServer stores without leaking credentials,
so that I can understand data-source configuration safely.

## Acceptance Criteria

1. Given a reachable authenticated GeoServer instance, when an MCP client requests store inventory, then the response includes data stores, coverage stores, and WMS stores where available, and each store includes instance ID, workspace, store name, store type, and enabled/disabled status when available.
2. Given store metadata includes sensitive connection details, when the store response is produced, then passwords, tokens, JDBC credential values, and configured sensitive fields are redacted.
3. Given a GeoServer version or endpoint does not expose a store category, when store inventory is requested, then the response records unavailable or unsupported information with a reason code.

## Tasks / Subtasks

- [x] Add store inventory domain model. (AC: 1, 2)
  - [x] Include instance ID, workspace, store name, resource ID, store type, enabled state, and optional REST href.
  - [x] Export the model from the shared domain boundary.
- [x] Extend safe GeoServer REST access. (AC: 1, 3)
  - [x] Add a read-only `list_stores` helper for data stores, coverage stores, and WMS stores.
  - [x] Route requests through the existing safe GET-only `get_json` path.
  - [x] Reject unsupported store categories before network access.
- [x] Implement store inventory service. (AC: 1, 2, 3)
  - [x] Reuse workspace inventory to discover per-instance workspace names.
  - [x] Query data store, coverage store, and WMS store endpoints per workspace.
  - [x] Preserve successful store results when one instance, workspace, or store category fails.
  - [x] Map malformed store payloads and unavailable categories to structured reason-code errors.
  - [x] Redact secrets from names, hrefs, errors, and serialized output.
- [x] Extend `list_catalog` MCP routing. (AC: 1, 2, 3)
  - [x] Support `resource_types=["stores"]`.
  - [x] Preserve `instances` and `workspaces` behavior.
  - [x] Keep mixed resource-type requests unsupported until request-scoped caching is implemented.
- [x] Update documentation. (AC: 1)
  - [x] Update README tool capability text to include store inventory.
- [x] Run and document the quality gate. (AC: all)
  - [x] Run focused unit tests for REST client, inventory service, MCP `list_catalog`, and read-only guardrails.

### Review Findings

- None in this implementation pass.

## Dev Notes

### Source Context

- Story source: `_bmad-output/planning-artifacts/epics.md` Story 2.3.
- Previous story source: `_bmad-output/implementation-artifacts/2-2-list-workspaces-across-instances.md`.

### Architecture Requirements

- Continue extending `list_catalog`; do not add a separate store MCP tool.
- Business orchestration belongs under `src/geoserver_mcp/services/`.
- MCP SDK imports stay under `src/geoserver_mcp/adapters/mcp/`.
- GeoServer REST calls stay behind the safe GET-only adapter.
- User-visible output must stay redacted and use the shared top-level response shape.
- Do not expose mutation operations or raw endpoint proxying.

### Implementation Guidance

- Use GeoServer REST store listing endpoints under `rest/workspaces/{workspace}/`.
- Normalize common GeoServer shapes for `dataStores.dataStore`, `coverageStores.coverageStore`, and `wmsStores.wmsStore`.
- Treat malformed successful responses as `parse_error`.
- Return `partial` when useful store results exist alongside failed categories or instances.

### Anti-Patterns To Avoid

- Do not return full connection parameter maps or raw GeoServer store detail payloads.
- Do not fail the whole store inventory request because one category is unavailable.
- Do not add layer, style, resource detail, OGC, diagnostics, or cache behavior in this story.

## Project Structure Notes

Story 2.3 expands catalog inventory from workspaces to store categories. It intentionally lists stores without fetching detailed connection configuration, keeping sensitive metadata out of the response surface.

## References

- [Source: epics.md Story 2.3](../planning-artifacts/epics.md)
- [Previous story: Story 2.2 workspace inventory](2-2-list-workspaces-across-instances.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- 2026-06-22: Implemented store inventory domain model, REST client helper, service aggregation, MCP routing, and README tool documentation.
- 2026-06-22: Focused tests passed: `.\.venv\Scripts\uv.exe run pytest tests\unit\test_geoserver_rest_client.py tests\unit\test_inventory_service.py tests\unit\test_mcp_list_catalog.py tests\unit\test_read_only_safety.py` with `UV_CACHE_DIR`, `TEMP`, and `TMP` scoped to workspace paths.
- 2026-06-22: `.\.venv\Scripts\uv.exe run ruff check src tests` passed.

### Completion Notes List

- Added `StoreInventoryItem` domain model.
- Added `GeoServerRestClient.list_stores()` for data stores, coverage stores, and WMS stores.
- Added store inventory service that reuses workspace discovery and records per-category failures.
- Extended `list_catalog` to support `resource_types=["stores"]`.
- Updated README MCP tool documentation.

### File List

- README.md
- _bmad-output/implementation-artifacts/2-3-list-stores-with-safe-metadata-redaction.md
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

- 2026-06-22: Created, implemented, tested, and marked Story 2.3 done.
