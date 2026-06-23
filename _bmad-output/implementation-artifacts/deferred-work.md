# Deferred Work

## Deferred from: code review of 2-4-list-layers-and-layer-groups (2026-06-23)

- Store inventory reuses redacted workspace names for REST calls. `_workspace_item()` redacts workspace names before `list_store_inventory()` uses `workspace.name` for follow-up store REST requests, so a workspace name overlapping a configured secret can target `[REDACTED]` paths. Deferred because this is pre-existing Story 2.3 behavior, not caused by Story 2.4.
