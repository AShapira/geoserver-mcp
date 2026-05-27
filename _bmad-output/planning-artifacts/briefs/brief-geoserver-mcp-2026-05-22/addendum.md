# Addendum: GeoServer MCP Product Context

## User-Provided Context

Audience: open-source GIS and IT professionals.

First use case: let an AI agent inspect and manage multiple GeoServer instances through MCP. Instances may run different GeoServer versions and have different deployment models. In some cases the GeoServer data directory is available, but this is not guaranteed. Some instances use filesystem-backed configuration, while others use PostGIS-backed stores.

Expected capabilities: list workspaces, stores, layers, styles, services, capabilities, and usage statistics, then help diagnose configuration issues.

Source material: no formal docs yet. Relevant inputs include GeoServer REST API docs, OGC service specs, and existing MCP SDK examples.

Stakes: this brief should drive the full BMAD PRD and architecture, not remain a quick note.

Initial posture: support multiple GeoServer connections, probably configured by local config file or environment variables. Start read-only, then later support safe write/admin actions.

## Fast Path Clarifications

- Primary persona: all target users matter, but GeoServer administrators are first and most important.
- MVP: inventory and diagnostics. Usage statistics should be added in future steps.
- Access model: HTTP/HTTPS access with administrator or equivalent permissions is granted. Local data-directory access exists in many cases but is not guaranteed, so the product should use it when available without depending on it.
- Configuration: support both configuration files and environment variables.
- Authentication: start with basic auth.
- Future management: CRUD is the most important future write/admin capability.
- Positioning: GeoServer operations assistant for AI agents, and also a diagnostic and governance tool.

## Source Grounding Notes

- GeoServer stable REST documentation covers catalog and service-management resources such as workspaces, stores, layers, styles, layer groups, and service settings.
- GeoServer monitoring/usage statistics are extension-dependent. The monitoring extension tracks requests, can persist request data, and exposes query/reporting surfaces when installed and configured.
- MCP has official SDKs for multiple languages, including TypeScript and Python; the implementation choice should be made during architecture after PRD scope is stable.
