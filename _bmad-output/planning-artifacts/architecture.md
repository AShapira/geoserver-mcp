---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments:
  - "C:\\Alex\\work\\geoserver-mcp\\_bmad-output\\planning-artifacts\\prds\\prd-geoserver-mcp-2026-05-25\\prd.md"
  - "C:\\Alex\\work\\geoserver-mcp\\_bmad-output\\planning-artifacts\\briefs\\brief-geoserver-mcp-2026-05-22\\brief.md"
  - "C:\\Alex\\work\\geoserver-mcp\\_bmad-output\\planning-artifacts\\research\\technical-dockerized-geoserver-mcp-server-architecture-options-research-2026-05-27.md"
workflowType: 'architecture'
project_name: 'geoserver-mcp'
user_name: 'Alex'
date: '2026-05-27'
lastStep: 8
status: 'complete'
completedAt: '2026-05-27'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Workflow Initialization

Architecture workflow initialized on 2026-05-27.

### Input Documents Loaded

- PRD: `C:\Alex\work\geoserver-mcp\_bmad-output\planning-artifacts\prds\prd-geoserver-mcp-2026-05-25\prd.md`
- Product brief: `C:\Alex\work\geoserver-mcp\_bmad-output\planning-artifacts\briefs\brief-geoserver-mcp-2026-05-22\brief.md`
- Technical research: `C:\Alex\work\geoserver-mcp\_bmad-output\planning-artifacts\research\technical-dockerized-geoserver-mcp-server-architecture-options-research-2026-05-27.md`

### Initialization Notes

- PRD exists and is sufficient to start architecture.
- No UX design document was found.
- No project context document was found.
- Technical research is complete and recommends a Dockerized Python modular monolith using the official Python MCP SDK.

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**

The PRD defines 20 functional requirements across five major capability areas:

- Dockerized MCP server runtime: startup, multi-instance config, connection checks.
- GeoServer inventory: instances, workspaces, stores, layers, layer groups, styles, service capabilities, and resource detail.
- Diagnostics and governance: findings, instance comparison, partial-access reporting, consolidated reports.
- Optional Data Directory inspection: configured read-only filesystem evidence when available.
- MCP agent interface and safety: read-only tools/resources, mutation prevention, secret handling, guided prompts.

Architecturally, this points to a backend integration service, not a UI-heavy application. The core system must normalize GeoServer REST, OGC capabilities, and optional filesystem evidence into stable internal models before exposing MCP responses.

**Non-Functional Requirements:**

Key NFRs shaping architecture:

- Security: no credential leakage, no sensitive store metadata exposure.
- Safety: v1 must be read-only and must not invoke mutation endpoints.
- Reliability: one failed GeoServer instance must not block other instances.
- Transparency: every partial or unavailable result needs an explicit reason.
- Compatibility: support multiple GeoServer versions through capability detection.
- Performance: avoid repeated endpoint calls during a single inspection flow.
- Observability: log startup, config, request, parser, and diagnostic failures without leaking secrets.
- Portability: Dockerized server is the primary v1 target.

**Scale & Complexity:**

- Primary domain: backend integration, GIS operations, MCP server, GeoServer diagnostics.
- Complexity level: medium-high.
- Estimated architectural components: 9 core components.

The complexity is not high because of UI or data volume. It is high because of integration variability: multiple GeoServer versions, multiple OGC protocols, partial access, optional data-directory mounts, authentication failures, XML parsing, and agent-facing safety constraints.

### Technical Constraints & Dependencies

Known constraints and dependencies:

- Implementation direction: Python preferred.
- Runtime target: Dockerized server.
- MCP layer: official Python MCP SDK / FastMCP.
- GeoServer access: HTTP/HTTPS with basic auth for v1.
- GeoServer API strategy: REST and OGC capabilities are primary evidence sources.
- Data Directory: optional read-only enrichment, never required.
- Storage: no product-owned database in v1.
- Security: no generic HTTP proxy, no mutation tools, no arbitrary filesystem reader.
- Testing: pytest, HTTP mocks, and Dockerized GeoServer fixtures.
- Future scope: catalog CRUD, usage statistics, broader auth models, monitoring extension, and governance snapshots.

### Cross-Cutting Concerns Identified

- Agent-facing API contract stability.
- Read-only safety and mutation prevention.
- Secret redaction across logs, reports, and MCP outputs.
- SSRF prevention through configured GeoServer target allowlisting.
- Safe XML parsing for OGC capabilities and Data Directory files.
- Partial-success behavior across multiple instances.
- Diagnostic reason-code taxonomy.
- GeoServer version and endpoint compatibility.
- Optional evidence sources with explicit source attribution.
- Docker configuration, secrets, and read-only mounts.
- Test fixture realism using real GeoServer containers.

## Starter Template Evaluation

### Primary Technology Domain

Backend/API integration service based on project requirements analysis.

This is not a web app, mobile app, or full-stack product. It is a Dockerized Python MCP server that integrates with GeoServer REST, OGC capabilities endpoints, and optional read-only data-directory mounts.

### Starter Options Considered

**Option 1: `uv init --package` custom Python package scaffold**

This creates a modern `pyproject.toml` Python package foundation without imposing unrelated web-app structure. It gives us a clean base for a `src/` package, tests, Dockerfile, MCP server entrypoint, and domain-specific architecture.

Best fit because GeoServer MCP needs custom module boundaries: MCP adapter, GeoServer REST adapter, OGC parser, diagnostics, config/secrets, redaction, and Docker fixtures.

Sources:
- https://docs.astral.sh/uv/guides/projects/
- https://docs.astral.sh/uv/concepts/projects/init/
- https://docs.astral.sh/uv/concepts/projects/config/

**Option 2: Cookiecutter PyPackage**

A strong general Python package template with docs, typing, CI, and packaging defaults. Useful for a library-first project, but heavier than needed for this MCP server and likely to introduce template structure that we would immediately reshape.

Source:
- https://audrey.feldroy.com/articles/2026-02-17-Cookiecutter-PyPackage-v0.4.0

**Option 3: FastMCP single-file starter**

Good for a prototype, but too thin for this project. It would not establish the package structure, test fixture strategy, Dockerized config model, or domain boundaries needed by the PRD.

Sources:
- https://github.com/modelcontextprotocol/python-sdk
- https://github.com/fastmcp-me/fastmcp-python

### Selected Starter: Custom `uv init --package` Python Scaffold

**Rationale for Selection:**

Use a minimal Python package scaffold, then add project-specific architecture deliberately. This avoids overfitting to a generic template and keeps the first implementation story focused: initialize the package and Docker runtime around the architecture, not around someone else's app shape.

**Initialization Command:**

```powershell
uv init --package --name geoserver-mcp
```

If running inside the existing repo root, the implementation story should first check whether `uv init` can safely initialize in-place without overwriting BMAD artifacts. If needed, initialize in a temporary folder and copy the generated package structure intentionally.

**Architectural Decisions Provided by Starter:**

**Language & Runtime:**

- Python package project.
- `pyproject.toml` as the central project metadata file.
- Python version pinned by project config, recommended Python 3.12+ unless dependency checks require otherwise.

**Styling Solution:**

- Not applicable. No UI styling layer in v1.

**Build Tooling:**

- `uv` for dependency management, lockfile generation, local execution, and repeatable development setup.
- Dockerfile added by project, not generated by the starter.
- Use Docker best practices: pinned base image, `.dockerignore`, non-root runtime user, minimal runtime image.

Sources:
- https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/
- https://docs.docker.com/guides/python/containerize/

**Testing Framework:**

- Add `pytest` for unit and integration tests.
- Add `respx` for mocking `httpx` calls.
- Add Docker Compose or Testcontainers-style fixtures for real GeoServer integration tests.

**Code Organization:**

Recommended package structure after initialization:

```text
src/geoserver_mcp/
  __init__.py
  server.py
  config/
  domain/
  services/
  adapters/
    mcp/
    geoserver_rest/
    ogc/
    data_directory/
  diagnostics/
  reporting/
  security/
tests/
  unit/
  integration/
docker/
examples/
```

**Development Experience:**

- `uv run` for local commands.
- `ruff` for lint/format.
- `pytest` for tests.
- MCP Inspector/manual smoke tests for MCP tool behavior.
- Docker Compose fixture for GeoServer and optional PostGIS.
- No database, no broker, no Kubernetes requirement in v1.

**Note:** Project initialization using this command should be the first implementation story.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**

- Runtime: Python, packaged with `uv`.
- Python baseline: Python 3.13 for v1, not 3.14 yet.
- MCP SDK: official Python `mcp` SDK / FastMCP.
- Architecture style: Dockerized Python modular monolith with hexagonal boundaries.
- GeoServer integration: GET-only HTTP/HTTPS REST + OGC capabilities.
- Data model: normalized internal evidence/inventory/diagnostic models.
- Storage: no product-owned database in v1.
- Security: no generic HTTP proxy, no mutation tools, strict redaction.
- Testing: pytest + HTTP mocks + Dockerized GeoServer fixtures.

**Important Decisions (Shape Architecture):**

- MCP transport: Streamable HTTP primary, stdio optional for local/dev compatibility.
- HTTP client: `httpx.AsyncClient`.
- Config: config file plus environment variables; secrets referenced indirectly.
- Validation: Pydantic / pydantic-settings.
- XML parsing: safe parser configuration; exact parser finalized in implementation patterns.
- Caching: request-scoped in-memory cache only.
- Docker: pinned base image, non-root user, read-only config/data mounts.

**Deferred Decisions (Post-MVP):**

- Catalog CRUD/write operations.
- Usage statistics and monitoring-extension integration.
- OAuth/bearer/pluggable auth.
- Persistent database or historical snapshots.
- Kubernetes-specific deployment.
- Broad extension lifecycle management.

### Data Architecture

- No database in v1.
- Configuration is file/env based.
- Runtime inventory is computed on demand.
- Request-scoped cache prevents duplicate calls within one tool/report run.
- Internal models:
  - `GeoServerInstance`
  - `Evidence`
  - `CatalogResource`
  - `ServiceCapability`
  - `InspectionResult`
  - `DiagnosticFinding`
  - `ReasonCode`

### Authentication & Security

- GeoServer v1 auth: basic auth only.
- MCP server credentials: env vars or secret files, referenced by config.
- Outbound requests only to configured GeoServer instance base URLs.
- Redirects disabled or tightly controlled.
- No generic HTTP request tool.
- No arbitrary filesystem reader.
- Data Directory mounts must be read-only and path-contained.
- XML parsing must disable unsafe entity/network behavior.
- All user-visible outputs and logs pass through redaction.

### API & Communication Patterns

- MCP public surface uses task-level tools, not raw endpoint wrappers.
- Primary tool groups:
  - connection/status
  - catalog inventory
  - service capabilities
  - resource detail
  - diagnostics
  - instance comparison
  - report generation
  - optional data-directory status
- GeoServer communication:
  - REST for catalog/config inventory
  - OGC capabilities for advertised services
  - optional Data Directory evidence for enrichment
- Error handling uses structured reason codes:
  - `network_error`
  - `auth_failed`
  - `forbidden`
  - `not_found`
  - `unsupported_endpoint`
  - `disabled_service`
  - `parse_error`
  - `missing_data_directory`
  - `unreadable_data_directory`
  - `redacted`
  - `partial_result`
  - `unknown`

### Frontend Architecture

Not applicable for v1. No UI, no dashboard, no styling system.

### Infrastructure & Deployment

- Dockerized server is the product target.
- Primary transport: Streamable HTTP.
- Optional transport: stdio for local development/client compatibility.
- Docker image should use pinned Python base image.
- Runtime should run as non-root user.
- Config mounted read-only.
- Optional GeoServer Data Directory mounts read-only.
- Docker Compose fixture should include GeoServer and optional PostGIS.
- No Kubernetes requirement in v1.

### Decision Impact Analysis

**Implementation Sequence:**

1. `uv init --package --name geoserver-mcp`
2. Add Python package structure and MCP server entrypoint.
3. Add config/env/secrets loading.
4. Add safe GeoServer HTTP client.
5. Add `check_instances`.
6. Add REST inventory.
7. Add OGC capabilities parsing.
8. Add diagnostics model and reason codes.
9. Add comparison/reporting.
10. Add optional Data Directory status.
11. Add Dockerfile and Docker Compose fixtures.

**Cross-Component Dependencies:**

- Config model feeds HTTP client, MCP tools, Data Directory adapter, and redaction.
- HTTP client and OGC parser feed evidence models.
- Evidence models feed inventory and diagnostics.
- Diagnostics feed reports and MCP responses.
- Redaction wraps all outputs.
- Testing must cover each adapter plus end-to-end Docker fixture behavior.

### Version Verification Notes

- Python 3.14 is current, but Python 3.13 is selected for v1 to reduce dependency/ecosystem risk.
- `mcp` Python SDK latest found: 1.27.1 on PyPI.
- `httpx` latest found: 0.28.1.
- Pydantic v2 / pydantic-settings are selected for config validation and env/secrets loading.

Sources:
- https://www.python.org/doc/versions/
- https://pypi.org/project/mcp/
- https://pypi.org/pypi/httpx/
- https://docs.astral.sh/uv/concepts/projects/init/
- https://docs.docker.com/guides/python/containerize/

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:**

11 areas where AI agents could make different choices:

- Python module layout
- domain model naming
- MCP tool naming
- response schemas
- error/reason-code format
- config structure
- secret handling
- GeoServer adapter boundaries
- XML parsing behavior
- logging/redaction
- test placement and fixture strategy

### Naming Patterns

**Database Naming Conventions:**

No product-owned database in v1. Do not introduce database table, migration, ORM, or repository naming patterns until a future architecture decision adds persistence.

**API Naming Conventions:**

MCP tools use snake_case verb-noun names:

- `check_instances`
- `list_catalog`
- `get_resource_detail`
- `get_service_capabilities`
- `compare_instances`
- `diagnose_instance`
- `generate_report`
- `get_data_directory_status`

Do not create one tool per GeoServer REST endpoint.

Good:

```text
list_catalog(instance_id="prod", resource_types=["workspaces", "layers"])
```

Avoid:

```text
get_geoserver_rest_workspaces_json()
call_geoserver_endpoint()
```

**Code Naming Conventions:**

Python code follows standard Python naming:

- modules/packages: `snake_case`
- functions/methods: `snake_case`
- variables: `snake_case`
- classes/models: `PascalCase`
- constants: `UPPER_SNAKE_CASE`

Domain names are stable and must be reused exactly:

- `GeoServerInstance`
- `InstanceConfig`
- `Evidence`
- `CatalogResource`
- `ServiceCapability`
- `InspectionResult`
- `DiagnosticFinding`
- `ReasonCode`

### Structure Patterns

**Project Organization:**

Use `src/` layout.

```text
src/geoserver_mcp/
  server.py
  config/
  domain/
  services/
  adapters/
  diagnostics/
  reporting/
  security/
tests/
  unit/
  integration/
docker/
examples/
```

Rules:

- MCP registration code lives under `adapters/mcp/`.
- GeoServer REST HTTP code lives under `adapters/geoserver_rest/`.
- OGC capabilities parsing lives under `adapters/ogc/`.
- Optional filesystem inspection lives under `adapters/data_directory/`.
- Business orchestration lives under `services/`.
- Domain models live under `domain/`.
- Redaction/path/URL safety helpers live under `security/`.
- No adapter imports from MCP-specific code except the MCP adapter.

**File Structure Patterns:**

Config examples live in `examples/`.

Docker/runtime files live in:

```text
Dockerfile
docker-compose.yml
docker/
```

Tests mirror architectural boundaries:

```text
tests/unit/test_config_*.py
tests/unit/test_redaction_*.py
tests/unit/test_reason_codes_*.py
tests/unit/test_ogc_*.py
tests/unit/test_geoserver_rest_*.py
tests/integration/test_*_geoserver.py
```

### Format Patterns

**API Response Formats:**

All MCP tool responses return structured objects with this conceptual shape:

```json
{
  "status": "success | partial | failed",
  "data": {},
  "findings": [],
  "errors": [],
  "metadata": {
    "tool": "check_instances",
    "generated_at": "ISO-8601",
    "instances": []
  }
}
```

Rules:

- Use `status` on every top-level response.
- Use `partial` when at least one instance failed but useful results exist.
- Use `errors` for operation-level failures.
- Use `findings` for diagnostic observations.
- Do not return raw GeoServer responses by default.

**Data Exchange Formats:**

- JSON fields use `snake_case`.
- Datetimes use ISO 8601 strings with timezone.
- `None` is allowed only for truly unavailable values; prefer explicit reason codes.
- Sensitive fields are redacted as `"***REDACTED***"`.

**Diagnostic Finding Format:**

```json
{
  "severity": "info | warning | error | critical",
  "reason_code": "auth_failed",
  "instance_id": "prod",
  "resource": {
    "type": "layer",
    "name": "workspace:layer_name"
  },
  "evidence": [],
  "message": "Human-readable explanation",
  "suggested_next_step": "Check credentials for this instance."
}
```

### Communication Patterns

**Event System Patterns:**

No event bus in v1. Do not introduce publish/subscribe, queues, background workers, or event sourcing.

**State Management Patterns:**

No durable application state in v1.

Allowed state:

- loaded config
- request-scoped cache
- in-memory HTTP client lifecycle
- per-call inspection context

Disallowed state:

- persistent inventory database
- scheduled snapshots
- background drift jobs
- hidden mutation state

### Process Patterns

**Error Handling Patterns:**

All external failures map to `ReasonCode`.

Initial reason codes:

- `network_error`
- `auth_failed`
- `forbidden`
- `not_found`
- `unsupported_endpoint`
- `disabled_service`
- `parse_error`
- `missing_data_directory`
- `unreadable_data_directory`
- `redacted`
- `partial_result`
- `unknown`

Rules:

- Do not raise raw adapter exceptions into MCP responses.
- Preserve technical details in logs only after redaction.
- Include evidence source where possible.
- Treat one instance failure as partial result, not global failure.

**Loading State Patterns:**

No UI loading states in v1. For long-running operations, use bounded execution and return partial results or timeout reason codes. Do not add async job queues in v1.

### Enforcement Guidelines

**All AI Agents MUST:**

- Keep v1 read-only.
- Use task-level MCP tools, not endpoint-wrapper tools.
- Put GeoServer HTTP calls only in `adapters/geoserver_rest/`.
- Put OGC XML parsing only in `adapters/ogc/`.
- Put optional Data Directory reads only in `adapters/data_directory/`.
- Return structured responses using the shared response pattern.
- Use `ReasonCode` for all known failures.
- Pass every user-visible output through redaction.
- Add or update tests when adding a new adapter, reason code, or response shape.
- Avoid introducing a database, queue, web UI, or mutation operation in v1.

**Pattern Enforcement:**

- Code review checks architectural boundaries.
- Tests cover redaction and reason-code mapping.
- PRs adding new MCP tools must document response shape and safety behavior.
- PRs adding GeoServer access must prove GET-only behavior.
- PRs adding filesystem access must prove path containment.

### Pattern Examples

**Good Examples:**

```python
class DiagnosticFinding(BaseModel):
    severity: Severity
    reason_code: ReasonCode
    instance_id: str
    resource: ResourceRef | None = None
    evidence: list[Evidence] = []
    message: str
    suggested_next_step: str | None = None
```

```python
async def check_instances(config: AppConfig) -> ToolResponse[InstanceStatusReport]:
    ...
```

**Anti-Patterns:**

```python
async def call_geoserver(url: str, method: str, body: dict | None = None):
    ...
```

```python
@app.tool()
def delete_layer(...):
    ...
```

```python
return raw_geoserver_response
```

## Project Structure & Boundaries

### Complete Project Directory Structure

```text
geoserver-mcp/
  README.md
  pyproject.toml
  uv.lock
  .python-version
  .gitignore
  .dockerignore
  Dockerfile
  docker-compose.yml
  AGENTS.md

  _bmad/
  _bmad-output/
  .agents/

  src/
    geoserver_mcp/
      __init__.py
      __main__.py
      server.py

      config/
        __init__.py
        models.py
        loader.py
        secrets.py

      domain/
        __init__.py
        enums.py
        evidence.py
        instances.py
        catalog.py
        capabilities.py
        diagnostics.py
        responses.py

      services/
        __init__.py
        instance_service.py
        inventory_service.py
        capability_service.py
        diagnostic_service.py
        comparison_service.py
        report_service.py

      adapters/
        __init__.py

        mcp/
          __init__.py
          app.py
          tools.py
          resources.py
          prompts.py
          schemas.py

        geoserver_rest/
          __init__.py
          client.py
          endpoints.py
          mappers.py
          errors.py

        ogc/
          __init__.py
          client.py
          parsers.py
          wms.py
          wfs.py
          wcs.py
          wmts.py

        data_directory/
          __init__.py
          inspector.py
          paths.py
          parsers.py

      diagnostics/
        __init__.py
        rules.py
        taxonomy.py
        severity.py

      reporting/
        __init__.py
        markdown.py
        json_report.py

      security/
        __init__.py
        redaction.py
        url_safety.py
        path_safety.py
        xml_safety.py

      observability/
        __init__.py
        logging.py

  tests/
    unit/
      test_config_loader.py
      test_secret_resolution.py
      test_redaction.py
      test_url_safety.py
      test_path_safety.py
      test_reason_codes.py
      test_response_shapes.py
      test_geoserver_rest_client.py
      test_ogc_parsers.py
      test_data_directory_paths.py
      test_diagnostic_rules.py

    integration/
      test_mcp_check_instances.py
      test_geoserver_inventory.py
      test_ogc_capabilities.py
      test_partial_access.py
      test_data_directory_optional.py

    fixtures/
      rest/
      ogc/
      data_directory/
      configs/

  docker/
    geoserver/
      README.md
      data_dir/
    postgis/
      init/

  examples/
    geoserver-mcp.yaml
    geoserver-mcp.env.example
    mcp-client-config.example.json

  docs/
    architecture/
    user-guide/
    developer-guide/
```

### Architectural Boundaries

**API Boundaries:**

The public API boundary is the MCP interface under `adapters/mcp/`.

Only `adapters/mcp/` imports the MCP SDK. Domain models, services, diagnostics, and GeoServer adapters must not depend on MCP SDK types.

**Component Boundaries:**

- `domain/` contains pure models and enums.
- `services/` orchestrates use cases.
- `adapters/` talks to external systems or protocols.
- `security/` owns redaction, URL safety, path safety, and XML safety.
- `diagnostics/` owns reason codes, severity, and rules.
- `reporting/` formats normalized results only.

**Service Boundaries:**

- `instance_service.py`: config-aware instance lookup and status orchestration.
- `inventory_service.py`: catalog inventory orchestration.
- `capability_service.py`: OGC capability orchestration.
- `diagnostic_service.py`: finding generation.
- `comparison_service.py`: multi-instance comparison.
- `report_service.py`: report assembly.

Services can call adapters and domain models. Adapters must not call services.

**Data Boundaries:**

No database in v1.

Data flows as:

```text
Config -> Services -> Adapters -> Evidence -> Domain Models -> Diagnostics -> MCP Response
```

Raw GeoServer responses stay inside adapters or test fixtures. MCP responses expose normalized models.

### Requirements to Structure Mapping

**Dockerized MCP Runtime: FR-1 to FR-3**

- `server.py`
- `adapters/mcp/app.py`
- `config/`
- `services/instance_service.py`
- `Dockerfile`
- `docker-compose.yml`
- `examples/`

**GeoServer Inventory: FR-4 to FR-10**

- `services/inventory_service.py`
- `domain/catalog.py`
- `adapters/geoserver_rest/`
- `adapters/ogc/`
- `security/redaction.py`

**Diagnostics and Governance: FR-11 to FR-14**

- `diagnostics/`
- `services/diagnostic_service.py`
- `services/comparison_service.py`
- `services/report_service.py`
- `reporting/`

**Optional Data Directory Inspection: FR-15 to FR-16**

- `adapters/data_directory/`
- `security/path_safety.py`
- `domain/evidence.py`
- `diagnostics/rules.py`

**MCP Agent Interface and Safety: FR-17 to FR-20**

- `adapters/mcp/tools.py`
- `adapters/mcp/resources.py`
- `adapters/mcp/prompts.py`
- `adapters/mcp/schemas.py`
- `security/redaction.py`
- `domain/responses.py`

### Integration Points

**Internal Communication:**

- MCP adapter calls services.
- Services call REST/OGC/Data Directory adapters.
- Adapters return `Evidence` and normalized domain models.
- Diagnostics consume models and evidence.
- Reporting consumes inventory, capabilities, and findings.

**External Integrations:**

- MCP clients connect through Streamable HTTP or stdio.
- GeoServer REST accessed over HTTP/HTTPS with basic auth.
- OGC capabilities accessed over HTTP/HTTPS.
- Optional Data Directory accessed through read-only Docker mounts.
- Optional PostGIS only appears as a GeoServer store fixture, not a direct app dependency.

**Data Flow:**

```text
MCP tool request
  -> adapters/mcp/tools.py
  -> service layer
  -> GeoServer REST / OGC / Data Directory adapters
  -> Evidence
  -> normalized domain models
  -> diagnostics and redaction
  -> ToolResponse
  -> MCP client
```

### File Organization Patterns

**Configuration Files:**

- Runtime config example: `examples/geoserver-mcp.yaml`
- Env example: `examples/geoserver-mcp.env.example`
- Project metadata: `pyproject.toml`
- Python version: `.python-version`
- Docker ignore rules: `.dockerignore`

**Source Organization:**

All importable application code lives under `src/geoserver_mcp/`.

No business logic in `server.py`; it only wires config, logging, services, and MCP app creation.

**Test Organization:**

- Unit tests mirror modules.
- Integration tests require Docker fixtures.
- Fixture payloads live under `tests/fixtures/`.
- Real GeoServer fixture setup lives under `docker/`.

**Asset Organization:**

No static assets in v1.

### Development Workflow Integration

**Development Server Structure:**

- `uv run geoserver-mcp` starts the MCP server.
- `uv run pytest` runs tests.
- `docker-compose up` starts local fixture services.

**Build Process Structure:**

- `uv` manages dependencies and lockfile.
- Dockerfile builds the runtime image.
- The image runs the package entrypoint, not a loose script.

**Deployment Structure:**

- Container receives config path via env var.
- Secrets come from env vars or mounted secret files.
- Config and optional Data Directory mounts are read-only.

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**

The major decisions work together:

- Python 3.13 + `uv` + official Python MCP SDK fit the Dockerized backend service target.
- `httpx.AsyncClient`, Pydantic settings, pytest, RESPX, and Docker fixtures are compatible with the selected Python stack.
- Streamable HTTP primary transport fits Dockerized server deployment; stdio remains available for local development/client compatibility.
- No database/no broker aligns with read-only v1 and request-scoped diagnostics.
- Hexagonal boundaries align with REST, OGC, Data Directory, MCP, config, security, and reporting adapters.

**Pattern Consistency:**

The patterns support the decisions:

- Snake_case MCP tool names match Python conventions.
- Structured `ToolResponse` shape supports partial results, diagnostics, and evidence.
- `ReasonCode` prevents agents from inventing incompatible error models.
- Redaction and safety rules cover the highest-risk cross-cutting concerns.

**Structure Alignment:**

The project structure supports the architecture:

- MCP SDK dependency is isolated under `adapters/mcp/`.
- GeoServer REST and OGC parsing are separate adapters.
- Optional Data Directory access has its own boundary.
- Services orchestrate use cases without depending on MCP-specific types.
- Tests mirror architectural boundaries.

### Requirements Coverage Validation ✅

**Feature Coverage:**

All PRD feature groups are architecturally supported:

- Dockerized MCP runtime: covered by `server.py`, MCP adapter, config, Dockerfile, compose files.
- GeoServer inventory: covered by REST/OGC adapters, inventory service, catalog/capability domain models.
- Diagnostics/governance: covered by diagnostics, comparison, reporting, reason codes.
- Optional Data Directory: covered by data-directory adapter and path safety.
- MCP interface/safety: covered by MCP adapter, schemas, redaction, read-only enforcement.

**Functional Requirements Coverage:**

- FR-1 to FR-3: covered by Docker/runtime/config/instance service.
- FR-4 to FR-10: covered by inventory/capability services and REST/OGC adapters.
- FR-11 to FR-14: covered by diagnostics/comparison/report services.
- FR-15 to FR-16: covered by Data Directory adapter and path safety.
- FR-17 to FR-20: covered by MCP adapter, response schemas, mutation prevention, redaction, prompts.

**Non-Functional Requirements Coverage:**

- Security: credential redaction, no generic HTTP proxy, URL allowlisting, path safety.
- Safety: GET-only v1, no mutation tools, no arbitrary filesystem reader.
- Reliability: partial results and per-instance reason codes.
- Transparency: evidence model and unavailable-information reporting.
- Compatibility: capability detection and version-aware fixture strategy.
- Performance: bounded async HTTP, request-scoped cache, summary/detail split.
- Observability: logging module and redaction requirements.
- Portability: Dockerized server and config/env model.

### Implementation Readiness Validation ✅

**Decision Completeness:**

Critical implementation blockers are decided:

- language/runtime
- package manager
- MCP SDK
- transport strategy
- config/secrets approach
- HTTP client
- architecture style
- response/error shape
- testing strategy
- Docker target

**Structure Completeness:**

The project tree is specific enough for implementation stories. It defines source layout, adapters, services, domain models, tests, fixtures, Docker assets, examples, and docs.

**Pattern Completeness:**

The patterns cover naming, structure, responses, reason codes, state, process, enforcement, and anti-patterns.

### Gap Analysis Results

**Critical Gaps:**

None.

**Important Gaps:**

- Exact XML parser choice is still open: `lxml` vs stdlib XML with safe parser rules.
- Exact response schemas need to be formalized during implementation.
- Exact GeoServer version compatibility matrix needs a first fixture choice.
- Exact Docker Compose fixture image tags need to be selected during implementation.
- Exact Streamable HTTP vs stdio runtime flags need to be defined in server configuration.

**Nice-to-Have Gaps:**

- CI pipeline shape.
- Documentation publishing strategy.
- MCP Inspector smoke-test workflow.
- Future governance snapshot storage strategy.

### Validation Issues Addressed

No blocking contradictions found. The open items are implementation-detail decisions that should be handled in early stories, especially the project scaffold and first vertical slice.

### Architecture Completeness Checklist

**Requirements Analysis**

- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed
- [x] Technical constraints identified
- [x] Cross-cutting concerns mapped

**Architectural Decisions**

- [x] Critical decisions documented with versions
- [x] Technology stack fully specified
- [x] Integration patterns defined
- [x] Performance considerations addressed

**Implementation Patterns**

- [x] Naming conventions established
- [x] Structure patterns defined
- [x] Communication patterns specified
- [x] Process patterns documented

**Project Structure**

- [x] Complete directory structure defined
- [x] Component boundaries established
- [x] Integration points mapped
- [x] Requirements to structure mapping complete

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION

**Confidence Level:** High

**Key Strengths:**

- Strong alignment between PRD, research, and architecture.
- Read-only safety is built into the architecture rather than bolted on later.
- Clear adapter boundaries reduce future agent implementation drift.
- No unnecessary database, queue, frontend, or Kubernetes complexity in v1.
- Testing strategy directly targets the highest-risk areas.

**Areas for Future Enhancement:**

- Persistent snapshots and drift detection.
- Usage statistics via GeoServer monitoring extension.
- Safe CRUD/admin operations.
- More authentication models.
- CI/CD and release automation.

### Implementation Handoff

**AI Agent Guidelines:**

- Follow all architectural decisions exactly as documented.
- Use implementation patterns consistently across all components.
- Respect project structure and boundaries.
- Do not introduce post-MVP capabilities into v1 stories.
- Refer to this document for all architectural questions.

**First Implementation Priority:**

Initialize the Python package scaffold safely in the existing repo:

```powershell
uv init --package --name geoserver-mcp
```

Then create the package/module skeleton, config model, Docker runtime stub, and first `check_instances` vertical slice.
