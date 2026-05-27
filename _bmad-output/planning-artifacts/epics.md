---
stepsCompleted: [1, 2, 3, 4]
status: 'complete'
completedAt: '2026-05-27'
inputDocuments:
  - "C:\\Alex\\work\\geoserver-mcp\\_bmad-output\\planning-artifacts\\prds\\prd-geoserver-mcp-2026-05-25\\prd.md"
  - "C:\\Alex\\work\\geoserver-mcp\\_bmad-output\\planning-artifacts\\architecture.md"
  - "C:\\Alex\\work\\geoserver-mcp\\_bmad-output\\planning-artifacts\\research\\technical-dockerized-geoserver-mcp-server-architecture-options-research-2026-05-27.md"
  - "C:\\Alex\\work\\geoserver-mcp\\_bmad-output\\planning-artifacts\\briefs\\brief-geoserver-mcp-2026-05-22\\brief.md"
---

# geoserver-mcp - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for geoserver-mcp, decomposing the requirements from the PRD, Architecture, Technical Research, and Product Brief into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: Users can start GeoServer MCP as a Docker container with no repository-local source checkout required after packaging.

FR2: Users can configure multiple GeoServer Instances, each with a stable name, base URL, basic-auth credential reference, and optional Data Directory path.

FR3: Users can ask the MCP server to check configured GeoServer Instances for reachability, authentication success, and basic server metadata.

FR4: Users can list configured GeoServer Instances with reachability status, reported version when available, base URL, supported inspected surfaces, and last inspection status.

FR5: Users can list workspaces for one GeoServer Instance or all configured GeoServer Instances.

FR6: Users can list data stores, coverage stores, and WMS stores where GeoServer exposes them through the available REST API.

FR7: Users can list layers and layer groups, including workspace relationship, type, enabled/advertised state when available, default style relationship, and related store/resource identifiers.

FR8: Users can list styles and inspect style relationships to layers where GeoServer exposes those relationships.

FR9: Users can inspect advertised Service Capabilities for supported OGC services, with v1 focusing on WMS, WFS, WCS, and WMTS where available.

FR10: Users can request detail for a specific Catalog Resource by GeoServer Instance and resource identifier.

FR11: Users can request Diagnostic Findings for one GeoServer Instance or all configured GeoServer Instances.

FR12: Users can compare two or more GeoServer Instances for version, service, capability, workspace, store, layer, style, and inspection-surface differences.

FR13: Users can see what GeoServer MCP could not inspect and why.

FR14: Users can request a consolidated read-only report for selected GeoServer Instances.

FR15: Users can configure a Data Directory path for a GeoServer Instance.

FR16: When a Data Directory is available, users can request diagnostics that use filesystem-backed configuration evidence.

FR17: AI clients can discover and invoke read-only MCP tools/resources for connection checks, inventory, detail lookup, comparison, and diagnostic reporting.

FR18: GeoServer MCP does not expose v1 tools that create, update, delete, reload, purge, or otherwise mutate GeoServer state.

FR19: GeoServer MCP does not expose configured passwords or sensitive connection secrets through tools, logs, reports, or diagnostic output.

FR20: GeoServer MCP provides MCP prompts or equivalent guidance for common operational flows: inventory estate, diagnose instance, compare instances, and inspect layer.

### NonFunctional Requirements

NFR1: Credentials and sensitive connection details must never be returned in tool responses, reports, or normal logs.

NFR2: v1 must be read-only by design and must not invoke GeoServer mutation endpoints.

NFR3: A failure on one GeoServer Instance must not prevent inventory or diagnostics for other configured instances.

NFR4: Every result that depends on partial access must explain what was inspected and what was unavailable.

NFR5: v1 should support multiple GeoServer versions through capability detection rather than assuming one uniform API surface.

NFR6: Inventory across multiple instances should avoid unnecessary repeated endpoint calls within a single user-request flow.

NFR7: The Dockerized server should produce operational logs for startup, configuration validation, request failures, and endpoint inspection errors without leaking secrets.

NFR8: The first implementation target is Dockerized server usage; local package execution is optional for development but not a v1 product requirement.

### Additional Requirements

- Use a custom `uv init --package --name geoserver-mcp` Python package scaffold as the first implementation story.
- Use Python 3.13 for v1, not Python 3.14.
- Use the official Python `mcp` SDK / FastMCP.
- Use a Dockerized Python modular monolith with hexagonal boundaries.
- Use Streamable HTTP as the primary MCP transport and stdio as an optional local/development transport.
- Use `httpx.AsyncClient` for GeoServer HTTP access.
- Use Pydantic / pydantic-settings for config validation and environment/secrets loading.
- Use GeoServer REST and OGC capabilities as primary evidence sources.
- Treat Data Directory access as optional read-only enrichment only.
- Do not introduce a product-owned database in v1.
- Do not introduce queues, background workers, event sourcing, a web UI, or Kubernetes-specific requirements in v1.
- Enforce task-level MCP tools rather than raw GeoServer endpoint wrappers.
- Isolate MCP SDK dependency under `adapters/mcp/`.
- Isolate GeoServer REST code under `adapters/geoserver_rest/`.
- Isolate OGC parsing under `adapters/ogc/`.
- Isolate optional filesystem inspection under `adapters/data_directory/`.
- Centralize redaction, URL safety, path safety, and XML safety under `security/`.
- Use structured top-level MCP responses containing `status`, `data`, `findings`, `errors`, and `metadata`.
- Use the architecture-defined `ReasonCode` taxonomy for all known external failures.
- Keep raw GeoServer responses inside adapters or test fixtures; do not return raw responses by default.
- Use request-scoped in-memory caching only.
- Use pytest for unit/integration tests and RESPX or equivalent HTTPX mocking for HTTP contract tests.
- Use Dockerized GeoServer fixtures and optional PostGIS fixtures for integration tests.
- Docker runtime should use pinned base image, non-root user, read-only config mounts, and read-only optional Data Directory mounts.
- The first vertical slice should create the scaffold, module skeleton, config model, Docker runtime stub, and `check_instances`.

### UX Design Requirements

None. No UX Design document exists, and v1 has no UI/dashboard scope.

### FR Coverage Map

FR1: Epic 1 - Dockerized server startup

FR2: Epic 1 - Multi-instance configuration

FR3: Epic 1 - Instance connectivity checks

FR4: Epic 2 - Instance summary inventory

FR5: Epic 2 - Workspace inventory

FR6: Epic 2 - Store inventory

FR7: Epic 2 - Layer and layer-group inventory

FR8: Epic 2 - Style inventory

FR9: Epic 3 - OGC service capability inventory

FR10: Epic 2 - Catalog resource detail lookup

FR11: Epic 4 - Diagnostic findings

FR12: Epic 6 - Instance comparison

FR13: Epic 4 - Partial-access reporting

FR14: Epic 4 - Diagnostic report generation

FR15: Epic 5 - Optional Data Directory configuration

FR16: Epic 5 - Data Directory enhanced diagnostics

FR17: Epic 1 - Read-only MCP tools/resources foundation

FR18: Epic 1 - Mutation prevention

FR19: Epic 1 - Safe secret handling

FR20: Epic 6 - Guided operational prompts

## Epic List

### Epic 1: Safe Dockerized MCP Runtime and Instance Connectivity

Users can run GeoServer MCP as a Dockerized server, configure multiple GeoServer instances, authenticate with basic auth, and ask an AI agent to check instance reachability and basic server status without exposing secrets or mutation capabilities.

**FRs covered:** FR1, FR2, FR3, FR17, FR18, FR19

**User outcome:** A GeoServer administrator can start the MCP server and confirm which configured GeoServer instances are reachable, authenticated, and safe to inspect.

### Epic 2: GeoServer Catalog Inventory

Users can inventory core GeoServer catalog resources across one or more configured instances, including workspaces, stores, layers, layer groups, styles, and resource detail.

**FRs covered:** FR4, FR5, FR6, FR7, FR8, FR10

**User outcome:** A GeoServer administrator or GIS professional can ask an AI agent what GeoServer publishes and receive structured, redacted, follow-up-friendly catalog information.

### Epic 3: OGC Service Capability Inspection

Users can inspect advertised OGC service capabilities for configured GeoServer instances, starting with WMS, WFS, WCS, and WMTS where available.

**FRs covered:** FR9

**User outcome:** A user can understand which services and capabilities are actually advertised by each GeoServer instance, separate from raw catalog configuration.

### Epic 4: Diagnostics, Partial Access, and Operational Reports

Users can request diagnostic findings, see what could not be inspected and why, and generate consolidated read-only operational reports for selected GeoServer instances.

**FRs covered:** FR11, FR13, FR14

**User outcome:** A GeoServer administrator can move from raw inventory to actionable operational understanding, including failures, missing access, parse problems, and configuration concerns.

### Epic 5: Optional Data Directory Evidence Enrichment

Users can configure optional read-only GeoServer Data Directory access and use it as an additional evidence source for diagnostics when available.

**FRs covered:** FR15, FR16

**User outcome:** Deployments that can mount the GeoServer Data Directory get deeper diagnostic evidence, while deployments without filesystem access still work normally.

### Epic 6: Multi-Instance Comparison and Guided Agent Workflows

Users can compare configured GeoServer instances and use guided MCP prompts/workflows for common operations such as estate inventory, instance diagnosis, instance comparison, and layer inspection.

**FRs covered:** FR12, FR20

**User outcome:** The MCP server becomes useful for higher-level AI-agent workflows, not just individual inspection calls.

## Epic 1: Safe Dockerized MCP Runtime and Instance Connectivity

Users can run GeoServer MCP as a Dockerized server, configure multiple GeoServer instances, authenticate with basic auth, and ask an AI agent to check instance reachability and basic server status without exposing secrets or mutation capabilities.

### Story 1.1: Initialize Dockerized Python MCP Server Scaffold

As a GeoServer MCP maintainer,
I want a Python package and Docker runtime scaffold,
So that the server can start consistently as the foundation for all future capabilities.

**Acceptance Criteria:**

**Given** the repository is empty except for BMAD artifacts
**When** the scaffold is initialized
**Then** the project contains a `uv`-managed Python package using the approved `src/geoserver_mcp/` layout
**And** the package exposes a `geoserver-mcp` entrypoint that starts without GeoServer configuration

**Given** the Docker runtime is built
**When** the container starts with minimal valid runtime settings
**Then** the MCP server process starts successfully
**And** the image runs as a non-root user
**And** the Dockerfile uses a pinned Python base image

**Given** tests are run
**When** the scaffold test suite executes
**Then** at least one smoke test proves the package imports and server app can be constructed

**Given** the initial scaffold is created
**When** repository quality checks are run
**Then** the project exposes a documented single command or small command set for running tests and code quality checks
**And** the checks include the scaffold smoke test
**And** formatting, linting, and type-checking expectations are documented or explicitly deferred

**Given** the Docker runtime is part of the scaffold
**When** the quality gate runs locally or in CI
**Then** the Docker image build is verified
**And** failures stop the quality gate with actionable output

**Given** the repository is ready for collaborative implementation
**When** CI configuration is inspected
**Then** an initial CI workflow exists or the story explicitly documents why CI is deferred
**And** the CI/local quality gate runs the same core checks used by developers

### Story 1.2: Load Multi-Instance Configuration and Secret References

As a GeoServer administrator,
I want to configure multiple GeoServer instances using a config file and environment-provided secrets,
So that the MCP server can inspect real deployments without hardcoding credentials.

**Acceptance Criteria:**

**Given** a valid config file with multiple instance definitions
**When** the server loads configuration
**Then** each instance has a unique ID, base URL, auth reference, and optional Data Directory path
**And** duplicate instance IDs fail validation with an actionable error

**Given** credentials are referenced through environment variables
**When** config is loaded
**Then** the resolved runtime config can authenticate requests
**And** secret values are not exposed in normal config display, logs, or validation errors

**Given** required fields are missing or invalid
**When** config validation runs
**Then** startup fails with structured validation errors
**And** no GeoServer network calls are attempted

### Story 1.3: Implement Safe GeoServer HTTP Client for Read-Only Access

As a GeoServer administrator,
I want the MCP server to make safe authenticated read-only GeoServer requests,
So that connectivity checks cannot accidentally mutate GeoServer state.

**Acceptance Criteria:**

**Given** a configured GeoServer instance with basic auth credentials
**When** the HTTP client performs a connectivity request
**Then** it uses HTTP/HTTPS GET-only access
**And** it applies configured timeouts
**And** it does not follow unsafe redirects by default

**Given** an outbound request target is not derived from a configured GeoServer base URL
**When** the HTTP client is asked to call it
**Then** the request is rejected before network access
**And** the result uses an appropriate reason code

**Given** the GeoServer response is 401, 403, 404, timeout, or malformed
**When** the client maps the result
**Then** it returns a structured error using the shared `ReasonCode` taxonomy
**And** raw adapter exceptions do not leak into MCP responses

### Story 1.4: Expose `check_instances` MCP Tool

As a GeoServer administrator,
I want an AI agent to check all configured GeoServer instances,
So that I can quickly understand which instances are reachable, authenticated, and inspectable.

**Acceptance Criteria:**

**Given** the MCP server is running with multiple configured instances
**When** an MCP client invokes `check_instances`
**Then** the response includes one status result per configured instance
**And** one failed instance does not prevent results for other instances

**Given** an instance is reachable and authenticated
**When** `check_instances` runs
**Then** the result includes reachability status and basic server metadata when available

**Given** an instance fails due to network, auth, forbidden, unsupported endpoint, or unexpected response
**When** `check_instances` runs
**Then** the result includes a structured reason code and human-readable explanation
**And** secrets are redacted from all output

### Story 1.5: Enforce Read-Only MCP Safety Boundary

As a GeoServer administrator,
I want v1 MCP tools to be read-only by construction,
So that connecting the MCP server to admin-level GeoServer credentials cannot mutate deployments.

**Acceptance Criteria:**

**Given** the MCP server registers its v1 tools
**When** the tool list is inspected
**Then** no create, update, delete, reload, purge, or mutation tool is exposed

**Given** a developer adds GeoServer REST adapter methods
**When** unit tests inspect the adapter contract
**Then** v1 adapter methods are limited to GET/read-only operations

**Given** a user asks for a mutation capability through the MCP server
**When** no v1 mutation tool exists
**Then** the server does not perform any GeoServer mutation
**And** guided responses or prompts identify mutation as unsupported in v1

### Story 1.6: Add Initial Docker Compose GeoServer Fixture

As a GeoServer MCP maintainer,
I want a local Docker Compose fixture with GeoServer,
So that the connectivity flow can be tested against a real GeoServer container.

**Acceptance Criteria:**

**Given** the repository includes Docker Compose fixture configuration
**When** the fixture stack starts
**Then** at least one GeoServer container is reachable from the MCP server container or local test process

**Given** test credentials are configured for the fixture
**When** integration tests run against the fixture
**Then** `check_instances` can report a successful reachable/authenticated instance

**Given** the fixture uses test credentials
**When** examples and docs reference them
**Then** they are clearly marked as local-test-only
**And** production examples do not normalize default GeoServer credentials

## Epic 2: GeoServer Catalog Inventory

Users can inventory core GeoServer catalog resources across one or more configured instances, including workspaces, stores, layers, layer groups, styles, and resource detail.

### Story 2.1: List Configured Instance Inventory Summary

As a GeoServer administrator,
I want to list all configured GeoServer instances with inspection status,
So that I can see which instances are available for catalog inventory.

**Acceptance Criteria:**

**Given** the MCP server has multiple configured instances
**When** an MCP client requests the instance inventory summary
**Then** the response includes each instance ID, base URL, reachability status, inspected surfaces, and unavailable information
**And** secret values are redacted

**Given** an instance cannot be reached or authenticated
**When** the instance summary is generated
**Then** the response includes a reason code for that instance
**And** other instances are still reported

### Story 2.2: List Workspaces Across Instances

As a GeoServer administrator,
I want to list workspaces for one or more GeoServer instances,
So that I can understand the top-level catalog organization.

**Acceptance Criteria:**

**Given** a reachable authenticated GeoServer instance
**When** an MCP client requests workspace inventory
**Then** the response includes workspace names and owning instance IDs
**And** each workspace includes identifiers needed for follow-up store/layer inspection

**Given** multiple instances are requested
**When** one instance fails
**Then** successful workspace results are still returned for other instances
**And** the failed instance is represented with a reason code

### Story 2.3: List Stores With Safe Metadata Redaction

As a GeoServer administrator,
I want to list GeoServer stores without leaking credentials,
So that I can understand data-source configuration safely.

**Acceptance Criteria:**

**Given** a reachable authenticated GeoServer instance
**When** an MCP client requests store inventory
**Then** the response includes data stores, coverage stores, and WMS stores where available
**And** each store includes instance ID, workspace, store name, store type, and enabled/disabled status when available

**Given** store metadata includes sensitive connection details
**When** the store response is produced
**Then** passwords, tokens, JDBC credential values, and configured sensitive fields are redacted

**Given** a GeoServer version or endpoint does not expose a store category
**When** store inventory is requested
**Then** the response records unavailable or unsupported information with a reason code

### Story 2.4: List Layers and Layer Groups

As a GeoServer administrator,
I want to list layers and layer groups with their relationships,
So that I can inspect what the GeoServer catalog publishes.

**Acceptance Criteria:**

**Given** a reachable authenticated GeoServer instance
**When** an MCP client requests layer inventory
**Then** the response includes layers with instance ID, name, workspace relationship when available, resource type, enabled/advertised state when available, default style relationship, and related store/resource identifiers

**Given** layer groups are available through the REST API
**When** layer inventory is requested
**Then** the response includes layer groups separately from individual layers

**Given** a layer references a missing or unavailable related resource detectable through available metadata
**When** layer inventory is normalized
**Then** a diagnostic-ready finding or warning is attached without failing the full inventory request

### Story 2.5: List Styles and Style Usage

As a GeoServer administrator,
I want to list styles and understand their layer relationships,
So that I can identify styling coverage and potential style issues.

**Acceptance Criteria:**

**Given** a reachable authenticated GeoServer instance
**When** an MCP client requests style inventory
**Then** the response includes style names, workspace relationship when available, owning instance ID, and usage relationships where GeoServer exposes them

**Given** layers have default or alternate styles
**When** style relationships are inspected
**Then** the response identifies default and alternate style usage when available

**Given** raw style content exists
**When** style inventory is requested
**Then** raw style content is not returned by default

### Story 2.6: Get Catalog Resource Detail

As a GeoServer administrator,
I want to request detailed information for a specific catalog resource,
So that I can inspect one workspace, store, layer, layer group, or style without dumping the whole catalog.

**Acceptance Criteria:**

**Given** a valid instance ID and catalog resource identifier
**When** an MCP client requests catalog resource detail
**Then** the response includes normalized details for that resource
**And** the response identifies the evidence source used, such as REST

**Given** requested details are unavailable due to GeoServer version, permissions, or unsupported endpoint
**When** detail lookup runs
**Then** the response includes missing-field notes and reason codes rather than failing with raw exceptions

**Given** the resource detail includes sensitive values
**When** the response is produced
**Then** sensitive values are redacted before returning to the MCP client

### Story 2.7: Add Request-Scoped Catalog Cache

As a GeoServer administrator,
I want catalog inventory requests to avoid redundant GeoServer calls within one operation,
So that multi-resource inventory is efficient without adding persistent storage.

**Acceptance Criteria:**

**Given** a single inventory operation needs the same GeoServer endpoint more than once
**When** request-scoped caching is enabled
**Then** the endpoint is fetched once within that operation
**And** later reads reuse the cached result

**Given** a new MCP tool invocation starts
**When** catalog inventory runs again
**Then** it does not rely on stale data from a prior invocation

**Given** caching is used
**When** results are returned
**Then** response metadata remains accurate about evidence source and inspection status

## Epic 3: OGC Service Capability Inspection

Users can inspect advertised OGC service capabilities for configured GeoServer instances, starting with WMS, WFS, WCS, and WMTS where available.

### Story 3.1: Implement Safe OGC Capabilities Fetching

As a GeoServer administrator,
I want the MCP server to fetch OGC capabilities documents safely,
So that advertised service metadata can be inspected without exposing unsafe HTTP/XML behavior.

**Acceptance Criteria:**

**Given** a configured GeoServer instance
**When** an OGC capabilities request is made
**Then** the request target is derived only from the configured GeoServer base URL
**And** unsupported or unavailable services return structured reason codes

**Given** an OGC capabilities response is XML
**When** the response is parsed
**Then** XML parsing uses safe parser settings that disable unsafe entity/network behavior
**And** malformed XML returns `parse_error` without leaking raw parser exceptions

**Given** a service capabilities request fails for one instance
**When** multiple instances are inspected
**Then** other instance results are still returned

### Story 3.2: Inspect WMS Capabilities

As a GeoServer administrator,
I want to inspect WMS capabilities for configured GeoServer instances,
So that I can understand advertised map-service layers and operations.

**Acceptance Criteria:**

**Given** WMS is available on a configured GeoServer instance
**When** an MCP client requests WMS capabilities
**Then** the response includes service availability, version when available, advertised layers when reasonably available, supported operations when available, evidence source, and parse status

**Given** WMS is disabled, forbidden, unavailable, or malformed
**When** WMS capabilities are requested
**Then** the response includes an appropriate reason code
**And** does not fail unrelated services or instances

### Story 3.3: Inspect WFS Capabilities

As a GeoServer administrator,
I want to inspect WFS capabilities for configured GeoServer instances,
So that I can understand advertised feature services and feature types.

**Acceptance Criteria:**

**Given** WFS is available on a configured GeoServer instance
**When** an MCP client requests WFS capabilities
**Then** the response includes service availability, version when available, advertised feature types when reasonably available, supported operations when available, evidence source, and parse status

**Given** WFS is disabled, forbidden, unavailable, or malformed
**When** WFS capabilities are requested
**Then** the response includes an appropriate reason code
**And** successful WMS or other service results remain available if requested in the same operation

### Story 3.4: Inspect WCS and WMTS Capabilities

As a GeoServer administrator,
I want to inspect WCS and WMTS capabilities where available,
So that coverage and tile-service exposure are visible alongside WMS and WFS.

**Acceptance Criteria:**

**Given** WCS or WMTS is available on a configured GeoServer instance
**When** an MCP client requests service capabilities
**Then** the response includes normalized WCS/WMTS availability, version when available, advertised resources when reasonably available, evidence source, and parse status

**Given** WCS or WMTS is not installed, disabled, unavailable, or malformed
**When** service capabilities are requested
**Then** the response records the unavailable service with a reason code
**And** does not treat optional service absence as a global failure

### Story 3.5: Expose Service Capability Inventory Tool

As a GIS professional,
I want an MCP tool that returns service capability inventory across configured instances,
So that an AI agent can answer what services are actually advertised by each GeoServer deployment.

**Acceptance Criteria:**

**Given** multiple configured GeoServer instances
**When** an MCP client invokes `get_service_capabilities`
**Then** the response includes requested service capability results grouped by instance and service type
**And** the response uses the shared top-level `status`, `data`, `findings`, `errors`, and `metadata` structure

**Given** some services or instances fail
**When** capability inventory is returned
**Then** the response status is `partial` when useful results exist
**And** unavailable services include reason codes and evidence metadata

**Given** raw capabilities XML is large
**When** capability inventory is returned
**Then** raw XML is not returned by default
**And** normalized capability summaries are returned instead

### Story 3.6: Add OGC Capabilities Fixtures and Parser Tests

As a GeoServer MCP maintainer,
I want fixture-backed tests for OGC capabilities parsing,
So that service parsing remains stable across service types and GeoServer versions.

**Acceptance Criteria:**

**Given** sample WMS, WFS, WCS, and WMTS capabilities fixtures exist
**When** parser tests run
**Then** each parser extracts the normalized fields required by the service capability model

**Given** malformed XML and disabled/unavailable service fixtures exist
**When** parser and client tests run
**Then** failures map to the correct reason codes

**Given** capabilities documents include sensitive or verbose raw content
**When** test responses are normalized
**Then** raw XML is not exposed by default in MCP response shapes

## Epic 4: Diagnostics, Partial Access, and Operational Reports

Users can request diagnostic findings, see what could not be inspected and why, and generate consolidated read-only operational reports for selected GeoServer instances.

### Story 4.1: Define Diagnostic Finding Model and Severity Taxonomy

As a GeoServer administrator,
I want diagnostics to use a consistent finding model,
So that AI agents and humans can understand operational issues without ambiguous error text.

**Acceptance Criteria:**

**Given** diagnostic findings are produced
**When** a finding is serialized
**Then** it includes severity, reason code, instance ID, optional affected resource, evidence, message, and suggested next step

**Given** a finding is generated from a known failure mode
**When** the diagnostic model maps the issue
**Then** it uses one of the approved reason codes
**And** unknown failures use `unknown` only when no more specific reason code applies

**Given** tests inspect the taxonomy
**When** new reason codes or severities are added
**Then** they are covered by tests and documented in the taxonomy module

### Story 4.2: Generate Diagnostics From Connectivity, Catalog, and Capability Evidence

As a GeoServer administrator,
I want the MCP server to turn inspection evidence into diagnostic findings,
So that I can understand what needs attention instead of reading raw inventory.

**Acceptance Criteria:**

**Given** connectivity evidence includes network, auth, forbidden, unsupported endpoint, or unexpected response failures
**When** diagnostics are generated
**Then** each failure becomes a diagnostic finding with severity and suggested next step

**Given** catalog or capability evidence includes missing related resources, disabled services, parse failures, or unsupported endpoints
**When** diagnostics are generated
**Then** findings are produced without failing the entire diagnostic request

**Given** a finding is based on partial or uncertain evidence
**When** it is returned
**Then** the message identifies the evidence source and avoids overstating certainty

### Story 4.3: Report Partial Access and Unavailable Information

As a GeoServer administrator,
I want to see what could not be inspected and why,
So that I can distinguish real configuration problems from missing permissions or unavailable evidence.

**Acceptance Criteria:**

**Given** an instance, service, endpoint, or data-directory path cannot be inspected
**When** the MCP server returns an inventory or diagnostic response
**Then** unavailable information is represented with a reason code and human-readable explanation

**Given** useful results exist alongside failures
**When** the MCP response is returned
**Then** the top-level status is `partial`
**And** successful results are preserved

**Given** unavailable information is due to optional evidence such as Data Directory access
**When** the response is returned
**Then** it is described as limited visibility, not as a global failure

### Story 4.4: Expose `diagnose_instance` MCP Tool

As a GeoServer administrator,
I want an MCP tool that diagnoses one or more GeoServer instances,
So that an AI agent can summarize operational issues from available evidence.

**Acceptance Criteria:**

**Given** configured instances have connectivity, catalog, and service capability evidence available
**When** an MCP client invokes `diagnose_instance`
**Then** the response includes diagnostic findings grouped by instance
**And** each finding includes severity, reason code, evidence, and suggested next step

**Given** one requested instance cannot be inspected
**When** diagnostics run for multiple instances
**Then** diagnostics for other instances still complete
**And** the failed instance is represented by diagnostic findings

**Given** diagnostic output includes endpoint URLs, store metadata, or credential-adjacent values
**When** the response is returned
**Then** user-visible output is redacted

### Story 4.5: Generate Consolidated Operational Report

As a GeoServer administrator,
I want a consolidated read-only report for selected GeoServer instances,
So that I can copy operational findings into handoff notes, tickets, or review documents.

**Acceptance Criteria:**

**Given** one or more instances are selected
**When** an MCP client requests a report
**Then** the report includes inventory summary, service capability coverage, diagnostic findings, and unavailable information

**Given** a report includes multiple instances
**When** some inspections fail
**Then** the report clearly separates successful inspection results, findings, and unavailable areas

**Given** sensitive data appears in source evidence
**When** the report is generated
**Then** all report output is redacted before return

### Story 4.6: Add Diagnostics and Report Test Coverage

As a GeoServer MCP maintainer,
I want tests for diagnostics, partial access, and report generation,
So that operational findings remain consistent as inventory coverage grows.

**Acceptance Criteria:**

**Given** fixture evidence for network failure, auth failure, forbidden access, parse error, disabled service, and missing resource exists
**When** diagnostic tests run
**Then** each fixture maps to the expected severity and reason code

**Given** mixed success/failure fixture data exists
**When** report tests run
**Then** the generated response preserves successful results and marks the top-level status as `partial`

**Given** fixture data includes sensitive values
**When** diagnostic and report tests run
**Then** no sensitive value appears in serialized findings, errors, or report output

## Epic 5: Optional Data Directory Evidence Enrichment

Users can configure optional read-only GeoServer Data Directory access and use it as an additional evidence source for diagnostics when available.

### Story 5.1: Configure Optional Data Directory Paths Per Instance

As a GeoServer administrator,
I want to optionally configure a Data Directory path for each GeoServer instance,
So that deployments with filesystem access can provide deeper evidence without making it mandatory.

**Acceptance Criteria:**

**Given** an instance config includes a Data Directory path
**When** configuration validation runs
**Then** the path is associated only with that instance
**And** the instance remains valid if no Data Directory path is configured

**Given** a configured Data Directory path is missing or unreadable
**When** the server validates or inspects the path
**Then** it reports `missing_data_directory` or `unreadable_data_directory`
**And** REST/OGC inspection still works for that instance

**Given** multiple instances are configured
**When** only some include Data Directory paths
**Then** Data Directory availability is reported per instance

### Story 5.2: Enforce Read-Only Path Safety for Data Directory Access

As a GeoServer administrator,
I want Data Directory inspection to be path-contained and read-only,
So that the MCP server cannot expose or modify arbitrary filesystem content.

**Acceptance Criteria:**

**Given** a Data Directory path is configured
**When** the Data Directory adapter reads files
**Then** reads are constrained to the configured path for that instance
**And** path traversal outside that directory is rejected

**Given** a Data Directory mount is configured in Docker examples
**When** the compose/runtime documentation is read
**Then** the mount is shown as read-only

**Given** a requested file path is outside the configured Data Directory
**When** inspection is attempted
**Then** the request is rejected before reading
**And** a structured reason code is returned

### Story 5.3: Report Data Directory Availability and Evidence Source

As a GeoServer administrator,
I want to know whether Data Directory evidence was available and used,
So that I can understand how complete the diagnostics are.

**Acceptance Criteria:**

**Given** an instance has a readable Data Directory
**When** Data Directory status is requested
**Then** the response reports the path as available without exposing unsafe host details

**Given** an instance has no configured Data Directory
**When** Data Directory status is requested
**Then** the response reports limited visibility rather than failure

**Given** diagnostics use Data Directory evidence
**When** findings are returned
**Then** the evidence source clearly identifies Data Directory evidence separately from REST or OGC evidence

### Story 5.4: Add Minimal Data Directory Diagnostic

As a GeoServer administrator,
I want at least one filesystem-backed diagnostic when Data Directory access is available,
So that the optional evidence path proves real value without expanding into exhaustive catalog-file analysis.

**Acceptance Criteria:**

**Given** a readable Data Directory exists for an instance
**When** Data Directory diagnostics run
**Then** the server performs a minimal supported diagnostic, such as detecting the expected top-level structure or presence of workspace/style configuration files

**Given** the expected minimal structure is unavailable or unreadable
**When** diagnostics run
**Then** the server returns a Data Directory-sourced diagnostic finding with severity, reason code, evidence, and suggested next step

**Given** Data Directory diagnostics are not exhaustive in v1
**When** results are returned
**Then** the response clearly avoids claiming complete filesystem validation

### Story 5.5: Add Data Directory Fixtures and Safety Tests

As a GeoServer MCP maintainer,
I want fixture-backed tests for Data Directory path safety and optional evidence,
So that filesystem inspection remains safe and predictable.

**Acceptance Criteria:**

**Given** fixture Data Directory structures exist
**When** Data Directory tests run
**Then** available, missing, unreadable, and no-config scenarios are covered

**Given** path traversal attempts exist in tests
**When** the Data Directory adapter validates paths
**Then** traversal is rejected before file access

**Given** diagnostic output includes Data Directory evidence
**When** serialized responses are tested
**Then** evidence source metadata is present
**And** unsafe host filesystem details are not exposed

## Epic 6: Multi-Instance Comparison and Guided Agent Workflows

Users can compare configured GeoServer instances and use guided MCP prompts/workflows for common operations such as estate inventory, instance diagnosis, instance comparison, and layer inspection.

### Story 6.1: Compare Instance Catalog and Capability Summaries

As a GeoServer administrator,
I want to compare two or more GeoServer instances,
So that I can identify confirmed differences and unknowns across environments.

**Acceptance Criteria:**

**Given** two or more configured instances have inventory and capability evidence available
**When** an MCP client requests instance comparison
**Then** the response compares version, service, capability, workspace, store, layer, style, and inspection-surface differences where available

**Given** one compared instance has partial or failed inspection results
**When** comparison results are generated
**Then** confirmed differences are separated from unknown differences caused by incomplete access

**Given** comparison output includes sensitive values
**When** the response is returned
**Then** all sensitive values are redacted

### Story 6.2: Expose `compare_instances` MCP Tool

As a DevOps/SRE user,
I want an MCP tool for comparing configured GeoServer instances,
So that an AI agent can help identify drift between environments.

**Acceptance Criteria:**

**Given** the MCP server has multiple configured instances
**When** an MCP client invokes `compare_instances` with selected instance IDs
**Then** the tool returns structured comparison results grouped by category
**And** the response uses the shared top-level response format

**Given** fewer than two valid instances are provided
**When** `compare_instances` runs
**Then** the tool returns a validation error without making unnecessary GeoServer requests

**Given** one instance fails during comparison
**When** at least one comparison category still has useful data
**Then** the response status is `partial`
**And** failure details are represented with reason codes

### Story 6.3: Add Estate Inventory Guided Prompt

As a GeoServer administrator,
I want a guided MCP prompt for estate inventory,
So that an AI agent follows the intended safe sequence of read-only tools.

**Acceptance Criteria:**

**Given** MCP prompts are supported by the selected client
**When** the estate inventory prompt is used
**Then** it guides the agent to check instances, collect catalog inventory, inspect service capabilities, and summarize unavailable information

**Given** prompt support is not available in a client
**When** users rely on tools directly
**Then** all underlying tools still work without prompt dependency

**Given** the prompt includes operational guidance
**When** the prompt is rendered
**Then** it does not instruct the agent to perform unsupported mutation actions

### Story 6.4: Add Instance Diagnosis Guided Prompt

As a GeoServer administrator,
I want a guided MCP prompt for diagnosing one instance,
So that an AI agent can collect evidence and produce a useful operational explanation.

**Acceptance Criteria:**

**Given** an instance ID is available
**When** the diagnosis prompt is used
**Then** it guides the agent to check connectivity, collect relevant catalog/capability evidence, run diagnostics, and summarize findings

**Given** evidence is partial or unavailable
**When** the prompt guides the agent response
**Then** the prompt instructs the agent to state uncertainty and unavailable evidence clearly

**Given** the user asks for write/admin repair actions
**When** the prompt guides the agent response
**Then** it identifies write/admin actions as unsupported in v1

### Story 6.5: Add Layer Inspection Guided Prompt

As a GIS professional,
I want a guided MCP prompt for inspecting a layer,
So that an AI agent can explain a layer's catalog, style, store, and service exposure context.

**Acceptance Criteria:**

**Given** a layer identifier and instance ID are provided
**When** the layer inspection prompt is used
**Then** it guides the agent to retrieve catalog resource detail, style relationships, related store information, and service capability visibility where available

**Given** any related metadata is unavailable
**When** the prompt guides the agent response
**Then** the prompt instructs the agent to separate confirmed facts from unavailable or unknown facts

**Given** store or connection metadata includes sensitive values
**When** the layer inspection workflow returns output
**Then** sensitive values are redacted

### Story 6.6: Add Comparison and Prompt Test Coverage

As a GeoServer MCP maintainer,
I want tests for comparison and guided workflow surfaces,
So that high-level agent workflows stay safe and consistent.

**Acceptance Criteria:**

**Given** fixture inventory and capability results from two instances
**When** comparison tests run
**Then** confirmed differences and unknown differences are represented separately

**Given** fixture data includes partial failures
**When** comparison tests run
**Then** the response status and reason codes match the shared response pattern

**Given** prompt definitions are registered
**When** MCP registration tests run
**Then** estate inventory, instance diagnosis, and layer inspection prompts are discoverable
**And** prompt text does not instruct mutation or unsupported v1 actions
