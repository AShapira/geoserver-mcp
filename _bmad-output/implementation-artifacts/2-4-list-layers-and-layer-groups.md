# Story 2.4: List Layers and Layer Groups

Status: review

## Story

As a GeoServer administrator,
I want to list layers and layer groups with their relationships,
so that I can inspect what the GeoServer catalog publishes.

## Acceptance Criteria

1. Given a reachable authenticated GeoServer instance, when an MCP client requests layer inventory, then the response includes layers with instance ID, name, workspace relationship when available, resource type, enabled/advertised state when available, default style relationship, and related store/resource identifiers.
2. Given layer groups are available through the REST API, when layer inventory is requested, then the response includes layer groups separately from individual layers.
3. Given a layer references a missing or unavailable related resource detectable through available metadata, when layer inventory is normalized, then a diagnostic-ready finding or warning is attached without failing the full inventory request.

## Tasks / Subtasks

- [x] Add layer and layer-group inventory domain models. (AC: 1, 2, 3)
  - [x] Include instance ID, name, resource ID, workspace, resource type, enabled state, advertised state, default style, store/resource identifiers, and optional REST href for layers.
  - [x] Include instance ID, name, resource ID, workspace, publishable layer names, and optional REST href for layer groups.
  - [x] Export the models from the shared domain boundary.
- [x] Extend safe GeoServer REST access. (AC: 1, 2)
  - [x] Add read-only helpers for `rest/layers.json` and `rest/layergroups.json`.
  - [x] Route requests through the existing safe GET-only `get_json` path.
- [x] Implement layer inventory service. (AC: 1, 2, 3)
  - [x] Query layer and layer-group endpoints per configured instance.
  - [x] Normalize common GeoServer list/detail summary shapes without returning raw payloads.
  - [x] Preserve useful layer or group results when one endpoint or instance fails.
  - [x] Map malformed successful payloads to structured parse errors.
  - [x] Attach warning findings for detectable missing related resource metadata.
  - [x] Redact secrets from names, hrefs, errors, findings, and serialized output.
- [x] Extend `list_catalog` MCP routing. (AC: 1, 2, 3)
  - [x] Support `resource_types=["layers"]`.
  - [x] Preserve `instances`, `workspaces`, and `stores` behavior.
  - [x] Keep mixed resource-type requests unsupported until request-scoped caching is implemented.
- [x] Update documentation. (AC: 1, 2)
  - [x] Update README tool capability text to include layer and layer-group inventory.
- [x] Run and document the quality gate. (AC: all)
  - [x] Run focused unit tests for REST client, inventory service, MCP `list_catalog`, and read-only guardrails.

### Review Findings

- None in this implementation pass.

## Dev Notes

### Source Context

- Story source: `_bmad-output/planning-artifacts/epics.md` Story 2.4.
- PRD source: `_bmad-output/planning-artifacts/prds/prd-geoserver-mcp-2026-05-25/prd.md` FR-7.
- Previous story source: `_bmad-output/implementation-artifacts/2-3-list-stores-with-safe-metadata-redaction.md`.

### Architecture Requirements

- Continue extending `list_catalog`; do not add a separate layer MCP tool.
- Business orchestration belongs under `src/geoserver_mcp/services/`.
- MCP SDK imports stay under `src/geoserver_mcp/adapters/mcp/`.
- GeoServer REST calls stay behind the safe GET-only adapter.
- User-visible output must stay redacted and use the shared top-level response shape.
- Do not expose mutation operations, raw endpoint proxying, or arbitrary REST targets.
- Keep no-database/no-persistent-state behavior; request-scoped caching remains Story 2.7.

### Implementation Guidance

- Use GeoServer REST catalog list endpoints `rest/layers.json` and `rest/layergroups.json`.
- Normalize common GeoServer list shapes: `layers.layer` and `layerGroups.layerGroup`.
- Layer summary metadata may be incomplete; include fields only when present and attach warning findings for missing resource/store relationships rather than failing the request.
- Derive workspace from qualified names such as `workspace:layer` when available, or from explicit `workspace` metadata if GeoServer returns it.
- Keep `resource_id` stable for follow-up inspection: prefer qualified layer/group names and fall back to the display name.
- Return `partial` when useful layer or layer-group results exist alongside failed endpoints or instances.

### Anti-Patterns To Avoid

- Do not fetch or return full layer configuration detail unless the list endpoint already provided safe summary fields.
- Do not fail the whole layer inventory request because layer groups are unavailable.
- Do not add style inventory, resource-detail lookup, OGC capabilities, diagnostics taxonomy expansion, or cache behavior in this story.

## Project Structure Notes

Story 2.4 expands catalog inventory from workspaces and stores to published catalog surfaces. It should mirror the Story 2.3 pattern: small domain models, adapter helpers, service normalization, MCP routing, docs, and focused tests.

## References

- [Source: epics.md Story 2.4](../planning-artifacts/epics.md)
- [Source: PRD FR-7](../planning-artifacts/prds/prd-geoserver-mcp-2026-05-25/prd.md)
- [Previous story: Story 2.3 store inventory](2-3-list-stores-with-safe-metadata-redaction.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- 2026-06-23: Created Story 2.4 artifact and moved sprint status to in-progress.
- 2026-06-23: Implemented layer and layer-group domain models, REST helpers, inventory service normalization, MCP routing, and README tool documentation.
- 2026-06-23: Focused tests passed: `.\.venv\Scripts\uv.exe run pytest tests\unit\test_geoserver_rest_client.py tests\unit\test_inventory_service.py tests\unit\test_mcp_list_catalog.py tests\unit\test_read_only_safety.py` with 41 passed.
- 2026-06-23: Quality checks passed: `.\.venv\Scripts\uv.exe run ruff check src tests`, `.\.venv\Scripts\uv.exe run ruff format --check src tests`, and full `.\.venv\Scripts\uv.exe run pytest` with 79 passed / 1 skipped.
- 2026-06-23: `git diff --check` reported only CRLF conversion warnings and no whitespace defects.

### Completion Notes List

- Added `LayerInventoryItem` and `LayerGroupInventoryItem` domain models.
- Added `GeoServerRestClient.list_layers()` and `GeoServerRestClient.list_layer_groups()` for safe read-only REST access.
- Added layer inventory service that returns separate `layers` and `layer_groups` collections, preserves partial results, and records warning findings for malformed related-resource metadata.
- Extended `list_catalog` to support `resource_types=["layers"]` while keeping mixed resource requests unsupported.
- Updated README MCP tool documentation.
- Ignored repo-local `.tmp/` validation output used for Windows pytest/uv runs.

### File List

- .gitignore
- README.md
- _bmad-output/implementation-artifacts/2-4-list-layers-and-layer-groups.md
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

- 2026-06-23: Created Story 2.4 and started implementation.
- 2026-06-23: Implemented, tested, and marked Story 2.4 ready for review.
