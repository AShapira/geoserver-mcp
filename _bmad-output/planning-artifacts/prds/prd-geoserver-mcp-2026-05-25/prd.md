---
title: "PRD: GeoServer MCP"
status: "draft"
created: "2026-05-25"
updated: "2026-05-27"
---

# PRD: GeoServer MCP

## 0. Document Purpose

This PRD defines the first product release of GeoServer MCP for downstream BMAD architecture, epics, stories, and implementation planning. It is based on the product brief at `C:\Alex\work\geoserver-mcp\_bmad-output\planning-artifacts\briefs\brief-geoserver-mcp-2026-05-22\brief.md`. Requirements are grouped by capability, use stable functional requirement IDs, and intentionally describe product behavior rather than implementation internals.

## 1. Vision

GeoServer MCP is a Dockerized open-source Model Context Protocol server that lets AI agents inspect and diagnose multiple GeoServer instances through a safe, structured, GeoServer-aware interface.

The product is for GIS and IT professionals who operate real GeoServer deployments. Its first responsibility is to help GeoServer administrators answer operational questions quickly: what instances exist, what each instance publishes, how versions and capabilities differ, what looks misconfigured, and which details could not be inspected because access, permissions, or extensions were unavailable.

The first release is read-only. It must earn trust before it manages anything. Future releases can add catalog CRUD and other admin actions, but v1 must establish reliable inventory, diagnostics, connection handling, and agent-facing contracts.

## 2. Target User

### 2.1 Primary Persona

The primary persona is a GeoServer administrator responsible for one or more GeoServer instances across environments, versions, and deployment styles. They understand GeoServer concepts, but they do not want to manually inspect every REST endpoint, OGC capabilities document, style reference, store configuration, and data-directory detail for each instance.

### 2.2 Secondary Personas

- GIS analyst: needs to understand available layers, services, styles, and capabilities without administering the server directly.
- DevOps/SRE: needs deployment health, configuration consistency, version visibility, credential-safe operation, and Docker-friendly runtime behavior.
- Developer/integrator: needs an agent-accessible GeoServer interface for application support, debugging, and automation planning.

### 2.3 Jobs To Be Done

- Inventory multiple GeoServer instances from one MCP server.
- Compare deployments across environments or versions.
- Diagnose missing, broken, inconsistent, or suspicious GeoServer configuration.
- Understand which OGC services and capabilities are actually exposed.
- Give an AI agent safe read-only access to GeoServer operational context.
- Know when an answer is limited by unavailable permissions, extensions, endpoints, or local filesystem access.

### 2.4 Non-Users For v1

- Users who need a full replacement for the GeoServer admin UI.
- Users who need write/admin automation in the first release.
- Users who can only provide unauthenticated public OGC access.
- Users who require usage statistics as a core v1 capability.

### 2.5 Key User Journeys

- **UJ-1. Admin inventories a mixed GeoServer estate.** A GeoServer administrator starts the Dockerized MCP server with a config file and environment-provided credentials. Through an AI agent, they ask what instances, versions, workspaces, stores, layers, styles, and services are present. The agent returns a structured inventory and identifies any instance it could not inspect.

- **UJ-2. Admin diagnoses a suspected publishing issue.** A layer appears broken or missing in one environment. The admin asks the agent to inspect the relevant instance. The MCP server gathers REST and OGC metadata, reports what layer, store, style, service, and capability information is available, and flags missing or inconsistent references where the available APIs support that conclusion.

- **UJ-3. DevOps compares staging and production.** A DevOps/SRE user asks the agent to compare two configured GeoServer instances. The MCP server reports version differences, service/capability differences, catalog differences, and data-directory availability without requiring write access.

- **UJ-4. Agent handles partial access honestly.** A GIS analyst asks for service capabilities across all configured instances. One instance lacks valid credentials and another lacks local data-directory access. The MCP server returns successful results where possible and explicitly marks unavailable information with reason codes.

## 3. Glossary

- **GeoServer MCP** - The product: a Dockerized MCP server exposing GeoServer inventory and diagnostics to AI agents.
- **GeoServer Instance** - One configured GeoServer deployment reachable by HTTP or HTTPS.
- **Instance Config** - User-provided configuration for a GeoServer Instance, including name, base URL, authentication reference, and optional data-directory path.
- **Data Directory** - The GeoServer filesystem configuration directory, optionally mounted into the Dockerized MCP server for additional inspection.
- **Catalog Resource** - A GeoServer workspace, store, layer, layer group, or style.
- **Service Capability** - Metadata advertised by OGC service capabilities endpoints such as WMS, WFS, WCS, or WMTS.
- **Inventory** - Structured read-only listing of GeoServer Instance metadata, Catalog Resources, and Service Capabilities.
- **Diagnostic Finding** - A structured observation about potential misconfiguration, inconsistency, missing access, or incomplete information.
- **Read-Only Mode** - v1 operating mode where GeoServer MCP does not create, update, delete, reload, or otherwise mutate GeoServer state.

## 4. Features

### 4.1 Dockerized MCP Server Runtime

**Description:** GeoServer MCP runs as a Dockerized server suitable for local developer use, workstation operations, or deployment beside other GIS tooling. It loads one or more GeoServer Instance definitions and exposes a read-only MCP interface to compatible AI clients.

**Functional Requirements:**

#### FR-1: Dockerized startup

Users can start GeoServer MCP as a Docker container with no repository-local source checkout required after packaging.

**Consequences:**
- The server starts with a mounted configuration file or equivalent environment configuration.
- Startup fails with actionable validation errors when required configuration is missing.
- Startup does not require direct GeoServer Data Directory access.

#### FR-2: Multi-instance configuration

Users can configure multiple GeoServer Instances, each with a stable name, base URL, basic-auth credential reference, and optional Data Directory path.

**Consequences:**
- Instance names are unique within one server configuration.
- Credentials can be supplied through environment variables.
- Optional Data Directory paths can be omitted per instance.

#### FR-3: Instance connectivity check

Users can ask the MCP server to check configured GeoServer Instances for reachability, authentication success, and basic server metadata.

**Consequences:**
- Results distinguish network failure, authentication failure, authorization failure, unsupported endpoint, and unexpected response.
- One failed instance does not prevent reporting on other configured instances.

### 4.2 GeoServer Inventory

**Description:** GeoServer MCP provides read-only inventory of the configured GeoServer estate. Inventory must be useful to an AI agent and a human reviewer, not just a pass-through of raw endpoint responses.

**Functional Requirements:**

#### FR-4: Instance summary inventory

Users can list configured GeoServer Instances with reachability status, reported version when available, base URL, supported inspected surfaces, and last inspection status.

**Consequences:**
- The summary identifies which instances are inspectable.
- The summary identifies which information was unavailable.

#### FR-5: Workspace inventory

Users can list workspaces for one GeoServer Instance or all configured GeoServer Instances.

**Consequences:**
- Results include the owning GeoServer Instance.
- Results preserve enough identifiers for follow-up store, layer, and style inspection.

#### FR-6: Store inventory

Users can list data stores, coverage stores, and WMS stores where GeoServer exposes them through the available REST API.

**Consequences:**
- Results identify store type, workspace, enabled/disabled status when available, and related connection metadata that is safe to expose.
- Sensitive connection details are redacted by default.

#### FR-7: Layer and layer-group inventory

Users can list layers and layer groups, including workspace relationship, type, enabled/advertised state when available, default style relationship, and related store/resource identifiers.

**Consequences:**
- Results support follow-up inspection by instance and layer name.
- Missing related resources are surfaced as Diagnostic Findings when detectable.

#### FR-8: Style inventory

Users can list styles and inspect style relationships to layers where GeoServer exposes those relationships.

**Consequences:**
- Results identify default and alternate style usage when available.
- Raw style contents are not dumped by default; users request them explicitly if supported.

#### FR-9: Service capability inventory

Users can inspect advertised Service Capabilities for supported OGC services, with v1 focusing on WMS, WFS, WCS, and WMTS where available.

**Consequences:**
- Results distinguish service unavailable, service disabled, unauthenticated/unauthorized, parse failure, and successful capability inspection.
- Results include advertised layers or feature types where reasonably available from capabilities documents.

#### FR-10: Catalog resource detail lookup

Users can request detail for a specific Catalog Resource by GeoServer Instance and resource identifier.

**Consequences:**
- Detail responses include source surface used, such as REST, OGC capabilities, or optional Data Directory.
- Detail responses include missing-field notes when GeoServer version or permissions prevent full inspection.

### 4.3 Diagnostics And Governance

**Description:** GeoServer MCP turns inventory into operationally useful Diagnostic Findings. v1 diagnostics are conservative: they report what can be inferred from accessible metadata and do not pretend to validate unavailable systems.

**Functional Requirements:**

#### FR-11: Configuration diagnostic findings

Users can request Diagnostic Findings for one GeoServer Instance or all configured GeoServer Instances.

**Consequences:**
- Findings include severity, affected instance, affected resource when applicable, evidence source, and explanation.
- v1 findings include unreachable instance, auth failure, unsupported endpoint, disabled service, missing related resource where detectable, uninspectable optional Data Directory, and parse failure.

#### FR-12: Instance comparison

Users can compare two or more GeoServer Instances for version, service, capability, workspace, store, layer, style, and inspection-surface differences.

**Consequences:**
- Comparison results separate confirmed differences from unknown differences caused by incomplete access.
- Comparison output is structured enough for an AI agent to summarize or ask follow-up questions.

#### FR-13: Partial-access reporting

Users can see what GeoServer MCP could not inspect and why.

**Consequences:**
- Every unavailable area includes a reason code and human-readable explanation.
- Missing optional Data Directory access is reported as limited visibility, not as a failure.

#### FR-14: Diagnostic report generation

Users can request a consolidated read-only report for selected GeoServer Instances.

**Consequences:**
- The report includes inventory summary, Diagnostic Findings, capability coverage, and unavailable information.
- The report is suitable for copying into issue trackers, PRD/architecture discussions, or operational handoff notes.

### 4.4 Optional Data Directory Inspection

**Description:** When a GeoServer Data Directory is mounted into the Dockerized MCP server and linked to an Instance Config, GeoServer MCP may use it to enrich diagnostics. Data Directory access is optional and never required for core inventory.

**Functional Requirements:**

#### FR-15: Optional Data Directory configuration

Users can configure a Data Directory path for a GeoServer Instance.

**Consequences:**
- The server validates whether the path is present and readable.
- The server reports unavailable or unreadable paths without blocking REST/OGC inspection.

#### FR-16: Data Directory enhanced diagnostics

When a Data Directory is available, users can request diagnostics that use filesystem-backed configuration evidence.

**Consequences:**
- Findings clearly mark Data Directory as the evidence source.
- REST/OGC-derived findings and Data Directory-derived findings remain distinguishable.
- [ASSUMPTION] v1 includes only minimal Data Directory diagnostics needed to prove the extension point, not exhaustive catalog-file analysis.

### 4.5 MCP Agent Interface And Safety

**Description:** GeoServer MCP exposes a stable agent-facing MCP interface. The interface must be predictable, structured, conservative, and explicit about safety boundaries.

**Functional Requirements:**

#### FR-17: Read-only MCP tools and resources

AI clients can discover and invoke read-only MCP tools/resources for connection checks, inventory, detail lookup, comparison, and diagnostic reporting.

**Consequences:**
- Tool and resource names are stable within v1 after release.
- Responses are structured and include instance identity, evidence source, status, and errors where relevant.

#### FR-18: Mutation prevention

GeoServer MCP does not expose v1 tools that create, update, delete, reload, purge, or otherwise mutate GeoServer state.

**Consequences:**
- User requests for CRUD or admin mutation receive a clear "not supported in v1" response.
- No GeoServer REST write methods are invoked by v1 tools.

#### FR-19: Safe secret handling

GeoServer MCP does not expose configured passwords or sensitive connection secrets through tools, logs, reports, or diagnostic output.

**Consequences:**
- Credentials are redacted in all user-visible output.
- Store connection metadata is redacted where it may contain credentials or sensitive infrastructure details.

#### FR-20: Guided operational prompts

GeoServer MCP provides MCP prompts or equivalent guidance for common operational flows: inventory estate, diagnose instance, compare instances, and inspect layer.

**Consequences:**
- Prompts guide agents toward the intended sequence of read-only tools.
- Prompts do not bypass Read-Only Mode.

## 5. Cross-Cutting Non-Functional Requirements

- **NFR-1 Security:** Credentials and sensitive connection details must never be returned in tool responses, reports, or normal logs.
- **NFR-2 Safety:** v1 must be read-only by design and must not invoke GeoServer mutation endpoints.
- **NFR-3 Reliability:** A failure on one GeoServer Instance must not prevent inventory or diagnostics for other configured instances.
- **NFR-4 Transparency:** Every result that depends on partial access must explain what was inspected and what was unavailable.
- **NFR-5 Compatibility:** v1 should support multiple GeoServer versions through capability detection rather than assuming one uniform API surface. [ASSUMPTION] Exact supported version range is deferred to architecture.
- **NFR-6 Performance:** Inventory across multiple instances should avoid unnecessary repeated endpoint calls within a single user-request flow. [ASSUMPTION] Specific caching and timeout budgets are deferred to architecture.
- **NFR-7 Observability:** The Dockerized server should produce operational logs for startup, configuration validation, request failures, and endpoint inspection errors without leaking secrets.
- **NFR-8 Portability:** The first implementation target is Dockerized server usage; local package execution is optional for development but not a v1 product requirement.

## 6. Non-Goals

- GeoServer MCP is not a replacement for the GeoServer admin UI.
- v1 does not perform CRUD or other write/admin operations.
- v1 does not manage GeoServer users, roles, or security configuration.
- v1 does not require local Data Directory access.
- v1 does not require usage statistics or monitoring-extension integration.
- v1 does not promise exhaustive extension support.
- v1 does not provide unauthenticated public OGC browsing as the primary workflow.
- v1 does not hide uncertainty; unknown or inaccessible information must remain explicit.

## 7. MVP Scope

### 7.1 In Scope

- Dockerized MCP server.
- Multiple GeoServer Instance configurations.
- HTTP/HTTPS access to GeoServer REST and OGC capabilities endpoints.
- Basic authentication.
- Config file and environment variable configuration.
- Read-only inventory for instances, workspaces, stores, layers, layer groups, styles, and Service Capabilities.
- Diagnostics based on available REST/OGC metadata.
- Instance comparison.
- Optional Data Directory configuration and minimal enhanced diagnostics.
- Secret redaction and partial-access reporting.

### 7.2 Out Of Scope For MVP

- Catalog CRUD and style upload/update. Deferred to the first write/admin milestone.
- Usage statistics. Deferred until monitoring/log access is designed.
- Bearer token, OAuth, or pluggable authentication.
- Security/user management.
- Cache management, reload, purge, and service mutation.
- Full extension lifecycle management.
- GUI or web dashboard.

## 8. API Contracts And Public Surface

GeoServer MCP's public surface is the MCP interface exposed to AI clients. v1 must define stable names and structured response contracts for read-only operations before implementation begins.

Required public operation groups:

- Instance connection and status.
- Catalog inventory.
- Service capability inventory.
- Catalog resource detail lookup.
- Instance comparison.
- Diagnostic finding/report generation.
- Optional Data Directory status and evidence reporting.

[ASSUMPTION] Exact MCP tool/resource names, response schemas, pagination behavior, and error-code taxonomy will be defined in architecture before epics/stories are generated.

## 9. Constraints And Guardrails

- The first product target is a Dockerized server.
- GeoServer access is assumed to be HTTP/HTTPS with administrator or administrator-equivalent basic auth.
- Data Directory access may exist in many deployments but cannot be assumed.
- v1 must never mutate GeoServer state.
- Output must preserve enough evidence for operators to trust findings.
- Output must avoid leaking credentials or sensitive connection values.
- Diagnostics must distinguish evidence-backed findings from unknowns.

## 10. Success Metrics

**Primary**

- **SM-1:** A user can configure at least two GeoServer Instances and obtain a combined inventory report. Validates FR-1 through FR-10.
- **SM-2:** A user can diagnose at least one intentionally misconfigured or partially inaccessible instance and receive structured findings with reason codes. Validates FR-11, FR-13, FR-14, FR-19.
- **SM-3:** A user can compare two instances and identify confirmed versus unknown differences. Validates FR-12 and NFR-4.

**Secondary**

- **SM-4:** The Dockerized server can run with credentials supplied through environment variables and without local Data Directory mounts. Validates FR-1, FR-2, FR-15.
- **SM-5:** User-visible output redacts credentials and sensitive connection details. Validates FR-19 and NFR-1.

**Counter-metrics**

- **SM-C1:** Do not maximize the number of exposed MCP tools at the expense of clarity. A smaller stable interface is preferable to a broad endpoint dump.
- **SM-C2:** Do not optimize for write/admin automation in v1. Read-only trust is the release gate.

## 11. Open Questions

1. Which GeoServer versions define the initial compatibility target?
2. Which MCP SDK/runtime should be used for implementation?
3. What is the exact v1 diagnostic finding taxonomy?
4. Should optional Data Directory diagnostics ship in v1 or only be designed in v1?
5. Which OGC services are mandatory for v1 inspection beyond WMS, WFS, WCS, and WMTS?
6. Should the Docker image include a sample config and local test compose stack?
7. What level of pagination, timeout, and caching behavior is required for large GeoServer estates?

## 12. Assumptions Index

- Optional Data Directory diagnostics in v1 are minimal and prove the extension point, not exhaustive filesystem analysis.
- Exact supported GeoServer version range is deferred to architecture.
- Specific caching and timeout budgets are deferred to architecture.
- Exact MCP tool/resource names, response schemas, pagination behavior, and error-code taxonomy will be defined in architecture before epics/stories are generated.

