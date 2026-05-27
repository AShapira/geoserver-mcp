# Addendum: GeoServer MCP PRD

## Source Inputs

The PRD is seeded from the product brief workspace:

- `C:\Alex\work\geoserver-mcp\_bmad-output\planning-artifacts\briefs\brief-geoserver-mcp-2026-05-22\brief.md`
- `C:\Alex\work\geoserver-mcp\_bmad-output\planning-artifacts\briefs\brief-geoserver-mcp-2026-05-22\addendum.md`
- `C:\Alex\work\geoserver-mcp\_bmad-output\planning-artifacts\briefs\brief-geoserver-mcp-2026-05-22\.decision-log.md`

## Initial Concern Scan

- Developer-product/API surface: MCP tools/resources become the public product interface.
- Integration density: GeoServer REST, OGC capabilities, optional filesystem data-directory access, and extension-specific capabilities.
- Security and safety: admin-equivalent credentials, read-only v1, future write/admin actions.
- Version compatibility: multiple GeoServer versions and deployment styles.
- Operational diagnostics: inventory, configuration consistency, missing resources, broken references, and capability visibility.
- Data governance: credentials, instance metadata, and possible exposure of layer/store details through agent interactions.

## PRD Fast Path Decisions

- No additional source context beyond the product brief before drafting.
- Working mode: Fast path.
- First implementation target: Dockerized server.
- v1 remains read-only and focused on inventory and diagnostics.
- Usage statistics remain future scope.
- CRUD/admin actions remain future scope, with catalog CRUD as the most important future milestone.

## Source Grounding Notes

- GeoServer REST documentation provides catalog and service-management surfaces, including resources such as workspaces, stores, layers, layer groups, styles, and service settings.
- GeoServer OGC service documentation provides capability surfaces for services such as WMS, WFS, WCS, and WMTS.
- MCP server concepts include tools, resources, and prompts; GeoServer MCP should treat these as the agent-facing public surface rather than exposing raw GeoServer endpoints directly.
