---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments:
  - "C:\\Alex\\work\\geoserver-mcp\\_bmad-output\\planning-artifacts\\prds\\prd-geoserver-mcp-2026-05-25\\prd.md"
workflowType: 'research'
lastStep: 1
research_type: 'technical'
research_topic: 'Dockerized GeoServer MCP server architecture options'
research_goals: 'Research architecture options for a Dockerized GeoServer MCP server based on the PRD. Focus on TypeScript vs Python MCP SDK, GeoServer REST/OGC API coverage, multi-instance config, diagnostics taxonomy, optional data-directory inspection, and testing strategy.'
user_name: 'Alex'
date: '2026-05-27'
web_research_enabled: true
source_verification: true
---

# Research Report: technical

**Date:** 2026-05-27
**Author:** Alex
**Research Type:** technical

---

## Research Overview

This technical research evaluates architecture options for a Dockerized GeoServer MCP server based on the GeoServer MCP PRD. It focuses on Python versus TypeScript MCP SDK choices, GeoServer REST and OGC integration, multi-instance configuration, diagnostic taxonomy, optional GeoServer Data Directory inspection, Docker deployment, and testing strategy.

The central finding is that GeoServer MCP should be implemented as a Dockerized Python modular monolith using the official Python MCP SDK, with a hexagonal architecture that keeps MCP transport, GeoServer REST, OGC capabilities, optional Data Directory inspection, config/secrets, diagnostics, and reporting behind explicit adapters. GeoServer REST and OGC capabilities should be the primary evidence sources; Data Directory access should be optional read-only enrichment.

The report recommends a read-only v1 built around normalized evidence, inventory, service capabilities, diagnostic findings, strict secret redaction, bounded HTTP inspection, and Docker-based integration tests. The full synthesis at the end of this document provides the decision-ready summary for the next BMAD step: architecture creation.

---

<!-- Content will be appended sequentially through research workflow steps -->

## Technical Research Scope Confirmation

**Research Topic:** Dockerized GeoServer MCP server architecture options
**Research Goals:** Research architecture options for a Dockerized GeoServer MCP server based on the PRD. Focus on TypeScript vs Python MCP SDK, GeoServer REST/OGC API coverage, multi-instance config, diagnostics taxonomy, optional data-directory inspection, and testing strategy.

**Technical Research Scope:**

- Architecture Analysis - design patterns, frameworks, system architecture
- Implementation Approaches - development methodologies, coding patterns
- Technology Stack - languages, frameworks, tools, platforms
- Integration Patterns - APIs, protocols, interoperability
- Performance Considerations - scalability, optimization, patterns

**Research Methodology:**

- Current web data with rigorous source verification
- Multi-source validation for critical technical claims
- Confidence level framework for uncertain information
- Comprehensive technical coverage with architecture-specific insights

**Scope Confirmed:** 2026-05-27

## Technology Stack Analysis

### Programming Languages

The practical v1 language choice is between TypeScript/Node.js and Python. Both are viable because MCP has official SDKs for both ecosystems. The official MCP SDK page lists Python as a Tier 1 SDK, and the official Python SDK README documents server features including tools, resources, prompts, stdio, SSE, and Streamable HTTP. The official TypeScript SDK is also an official SDK for MCP servers and clients and remains a mainstream choice for MCP server implementation.

For GeoServer MCP, the language decision should be driven by product shape:

- **TypeScript** is attractive if the project wants a Node-native MCP ecosystem, npm packaging, strong JSON-schema-oriented typing, and alignment with many existing MCP examples and developer tools.
- **Python** is attractive if the project expects heavier geospatial parsing, XML processing, diagnostics logic, local filesystem inspection, and future GIS/data tooling integration.

Recommendation for architecture: choose **Python** unless there is a strong preference for TypeScript in the target contributor base. The core product is a geospatial operations and diagnostics tool, not a frontend-adjacent developer tool, and Python has a strong practical fit for XML, HTTP, filesystem inspection, report generation, and geospatial-adjacent libraries. Keep the MCP interface language-agnostic so a future TypeScript client or bridge is not blocked.

_Popular Languages:_ Python and TypeScript are the primary candidates because both have official MCP SDK support.

_Emerging Languages:_ C#, Java, and other SDK ecosystems exist, but they are not the best v1 fit unless the project deliberately aligns with JVM/enterprise GeoServer internals. A Java implementation would be closer to GeoServer itself but further from current MCP implementation patterns and Python/TypeScript package ergonomics.

_Language Evolution:_ MCP SDKs are still evolving. The Python SDK README explicitly distinguishes current stable v1.x documentation from v2 pre-alpha work; the TypeScript SDK search result similarly notes v1.x as the recommended production line until v2 matures. Architecture should pin SDK major versions and avoid relying on pre-alpha APIs.

_Performance Characteristics:_ The workload is mostly network I/O, XML/JSON parsing, normalization, and diagnostics. Either Python async HTTP clients or Node.js can handle this. Performance bottlenecks are more likely to be GeoServer endpoint latency, GetCapabilities payload size, timeout policy, and repeated inventory calls than language runtime throughput.

_Sources:_ [MCP SDKs](https://modelcontextprotocol.io/docs/sdk), [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk), [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk), [MCP server concepts](https://modelcontextprotocol.io/docs/learn/server-concepts)

### Development Frameworks and Libraries

The MCP framework layer should be the official SDK rather than a wrapper-first framework. The Python SDK includes FastMCP examples and decorators for tools, resources, and prompts, including Streamable HTTP transport in the documented quickstart. That maps well to the PRD's Dockerized server target and agent-facing public surface. TypeScript has an official SDK and npm distribution, but architecture should verify the exact current package name and major version before implementation because MCP package naming has changed across SDK versions.

GeoServer access should be implemented as a small project-owned client layer over HTTP instead of binding the whole product to an existing third-party GeoServer wrapper. The GeoServer REST API is broad and includes both read and write surfaces; v1 must enforce read-only behavior deliberately. A project-owned client layer can expose only the safe read operations needed by the PRD and can normalize version differences, status codes, and response formats.

For Python, likely library categories:

- MCP server: official `mcp` Python SDK / FastMCP.
- HTTP: `httpx` with timeouts and async support.
- XML: `lxml` or Python stdlib `xml.etree.ElementTree`, with secure parser settings.
- Config: Pydantic settings or equivalent typed config validation.
- Testing: `pytest`, `respx` or similar HTTP mocking, Docker Compose for GeoServer fixtures.
- Reports: Markdown/JSON generation from internal diagnostic models.

For TypeScript, likely library categories:

- MCP server: official `@modelcontextprotocol/sdk`.
- HTTP: `fetch`, `undici`, or `axios`.
- XML: `fast-xml-parser` or equivalent.
- Config: `zod` or similar schema validation.
- Testing: `vitest` or `jest`, HTTP mocks, Docker Compose fixtures.

_Major Frameworks:_ Official MCP SDKs should be the only required MCP framework dependency. Avoid extra abstraction until the API contract stabilizes.

_Micro-frameworks:_ Use small libraries for HTTP, config validation, XML parsing, redaction, and tests. Do not introduce a web framework unless the selected MCP transport requires it.

_Evolution Trends:_ MCP server implementations are moving toward stable tool/resource/prompt contracts and Streamable HTTP support. The architecture should isolate transport setup from GeoServer domain logic so SDK/API churn is contained.

_Ecosystem Maturity:_ Python has an advantage for geospatial-adjacent and operations tooling. TypeScript has an advantage for npm distribution and schema-heavy developer tooling. Both SDKs are official, so ecosystem fit should decide.

_Sources:_ [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk), [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk), [MCP server concepts](https://modelcontextprotocol.io/docs/learn/server-concepts), [GeoServer REST docs](https://docs.geoserver.org/stable/en/user/rest/index.html)

### Database and Storage Technologies

GeoServer MCP v1 should not require its own database. The PRD's v1 scope is read-only inventory and diagnostics. Persistent application state would add operational burden without clear MVP value.

Recommended v1 storage model:

- Configuration is supplied through a mounted config file plus environment variables for secrets/overrides.
- Runtime inventory can be computed on demand.
- Optional in-memory request-scoped caching can prevent duplicate calls within a single tool invocation or report generation.
- Durable cache/database is deferred until there is a clear use case such as scheduled estate snapshots, historical comparison, usage statistics, or governance reporting.

GeoServer data stores such as PostGIS are inspected as GeoServer-managed configuration, not accessed directly by GeoServer MCP in v1. Direct database access would expand credentials, permissions, network reachability, data governance, and query-safety scope. The first release should inventory stores through GeoServer REST and only report redacted connection metadata.

Usage statistics are explicitly future scope. GeoServer's monitoring extension can track requests and persist monitoring data, but it is extension-dependent and should be discovered as an optional capability later, not assumed as part of the v1 storage model.

_Relational Databases:_ No product-owned relational database in v1. PostGIS appears as a GeoServer store type, not a direct MCP dependency.

_NoSQL Databases:_ No NoSQL dependency recommended for v1.

_In-Memory Databases:_ No Redis/Memcached dependency recommended. Prefer process-local request cache if needed.

_Data Warehousing:_ Not relevant to v1. Historical governance and usage analytics can revisit this later.

_Sources:_ [GeoServer REST docs](https://docs.geoserver.org/stable/en/user/rest/index.html), [GeoServer data directory](https://docs.geoserver.org/latest/en/user/datadirectory/index.html), [GeoServer monitoring extension](https://docs.geoserver.org/main/en/user/extensions/monitoring/)

### Development Tools and Platforms

The development platform should make Dockerized operation and real GeoServer fixture testing first-class.

Recommended baseline for a Python implementation:

- Python project managed with `uv` or a modern `pyproject.toml` workflow.
- Dockerfile builds a pinned runtime image.
- Docker Compose provides local test fixtures: GeoServer, optional PostGIS, and mounted data directory variations.
- Unit tests cover config parsing, redaction, response normalization, diagnostics taxonomy, and XML parsing.
- Integration tests run against one or more GeoServer containers.
- MCP Inspector is used during development to verify tool/resource/prompt behavior.

Recommended baseline for TypeScript if chosen:

- Node.js project with pinned package manager behavior.
- Dockerfile builds a pinned Node runtime image.
- Same Docker Compose fixture strategy.
- Unit/integration tests with TypeScript-native test framework.
- MCP Inspector for server verification.

The GeoServer test fixture should use official GeoServer Docker images where feasible. The official GeoServer Docker repository documents pulling images from `docker.osgeo.org/geoserver:<VERSION>` and warns users to change default passwords, which reinforces that the test stack must never normalize default production credentials as acceptable.

_IDE and Editors:_ No hard requirement; use standard Python or TypeScript editor support.

_Version Control:_ Git is assumed. PRD and BMAD artifacts should remain versioned once the repository is initialized.

_Build Systems:_ Docker build plus language-native packaging. Pin base images and dependency versions to reduce release drift.

_Testing Frameworks:_ Python: `pytest` plus HTTP mocking and Docker Compose integration tests. TypeScript: `vitest`/`jest` plus HTTP mocking and Docker Compose integration tests. Both should include MCP Inspector/manual smoke checks.

_Sources:_ [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk), [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk), [GeoServer Docker repository](https://github.com/geoserver/docker), [GeoServer REST API details](https://geoserver.org/geoserver/en/user/rest/api/details/)

### Cloud Infrastructure and Deployment

The PRD target is a Dockerized server, not a hosted SaaS. v1 should optimize for local and self-hosted deployment near the user's AI client and reachable GeoServer instances.

Recommended deployment shape:

- Single container running the MCP server.
- Mounted read-only config file.
- Credentials injected via environment variables or Docker secrets where available.
- Optional read-only mounts for GeoServer Data Directories.
- Network access to configured GeoServer base URLs.
- Health/startup validation that fails fast on invalid server configuration but does not require all GeoServer instances to be reachable at startup.

Kubernetes and cloud deployment should remain compatible but not drive v1 complexity. A stateless container with file/env configuration can later fit Docker Compose, Kubernetes, or a desktop MCP-client workflow. If Streamable HTTP is selected as the transport, the architecture must define host/port exposure and client compatibility. If stdio is selected, Docker invocation and client integration become more constrained.

_Major Cloud Providers:_ Not a v1 dependency. The product should run wherever Docker can reach GeoServer.

_Container Technologies:_ Docker is required by product direction; Docker Compose is recommended for development and test fixtures.

_Serverless Platforms:_ Not recommended. Long-lived MCP server behavior, local credentials, data-directory mounts, and network access to internal GeoServer instances fit containers better than serverless.

_CDN and Edge Computing:_ Not relevant to v1.

_Sources:_ [GeoServer Docker repository](https://github.com/geoserver/docker), [GeoServer Cloud Docker image architecture](https://geoserver.org/geoserver-cloud/developer-guide/docker-images/), [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

### Technology Adoption Trends

MCP is actively evolving, with official SDK support across multiple languages and growing attention to production failure modes. For this project, that means the architecture should avoid locking business logic directly to SDK-specific APIs. Keep GeoServer domain logic, diagnostics models, config parsing, and response schemas in project-owned modules, with a thin MCP adapter layer at the edge.

GeoServer itself has a mature REST API and OGC service model, but deployments vary. The REST docs describe resources for catalog and service management and support multiple representation formats. GeoServer's data directory docs explicitly say direct configuration-file access is not intended as the primary programmatic management path; REST should be preferred for programmatic access. Therefore, Data Directory inspection should be optional evidence-gathering, not the primary control plane.

The strongest architecture trend for this product is **contract-first normalization**: convert GeoServer-specific REST, OGC XML, and optional filesystem evidence into stable internal models, then expose those through MCP tools/resources. This avoids the anti-pattern of turning every GeoServer endpoint into an MCP tool.

_Migration Patterns:_ Start read-only with normalized inventory/diagnostics. Add write/admin operations only after the MCP contract, redaction, confirmation, and safety patterns are proven.

_Emerging Technologies:_ MCP Streamable HTTP support is relevant for a Dockerized server; architecture should confirm current client support before making it the only transport.

_Legacy Technology:_ GeoServer installations may span older versions. Capability detection and graceful degradation are safer than assuming every endpoint exists.

_Community Trends:_ MCP server authors commonly expose tools for model-controlled actions, resources for contextual data, and prompts for guided workflows. GeoServer MCP should use all three carefully, but v1 should treat tools as the primary reliable interaction surface because client support for resources/prompts can vary.

_Sources:_ [MCP server concepts](https://modelcontextprotocol.io/docs/learn/server-concepts), [MCP SDKs](https://modelcontextprotocol.io/docs/sdk), [GeoServer REST docs](https://docs.geoserver.org/stable/en/user/rest/index.html), [GeoServer data directory structure](https://docs.geoserver.org/latest/en/user/datadirectory/structure.html), [GeoServer REST API details](https://geoserver.org/geoserver/en/user/rest/api/details/)

**User Direction:** Python is preferred for the first implementation unless architecture research later surfaces a strong reason to reverse that choice.

## Integration Patterns Analysis

### API Design Patterns

GeoServer MCP should use a **normalized adapter pattern** rather than a one-to-one REST endpoint wrapper. GeoServer REST exposes many catalog and service-management resources and supports both read and write operations. The v1 PRD is read-only, so the MCP surface must deliberately expose only safe read operations even when underlying REST endpoints support PUT, POST, or DELETE.

Recommended integration layers:

1. **MCP adapter layer** - Python MCP tools/resources/prompts, stable public names, structured responses.
2. **Domain service layer** - inventory, diagnostics, comparison, reporting, redaction.
3. **GeoServer client layer** - authenticated HTTP calls to REST and OGC endpoints.
4. **Evidence adapters** - REST evidence, OGC capabilities evidence, optional Data Directory evidence.
5. **Normalization layer** - converts GeoServer version/format differences into internal models.

The API design should be operation-centered:

- `check_instances`
- `list_catalog`
- `get_resource_detail`
- `get_service_capabilities`
- `compare_instances`
- `diagnose_instance`
- `generate_report`

This is preferable to endpoint-centered tools such as `get_layers_json`, `get_workspaces_xml`, or `call_rest_endpoint`, because the agent should reason over GeoServer concepts and diagnostic findings rather than raw protocol mechanics.

_RESTful APIs:_ GeoServer REST is the primary configuration/inventory API. It is authenticated, status-code driven, and documented through endpoint resources such as workspaces, stores, layers, layer groups, styles, and service settings. Use GET-only operations in v1.

_GraphQL APIs:_ Not relevant. Adding GraphQL would create a second public API without solving the core MCP/GeoServer problem.

_RPC and gRPC:_ Not relevant for GeoServer integration. MCP itself is already the agent-facing invocation protocol.

_Webhook Patterns:_ Not relevant for v1 because the product is on-demand read-only inspection, not event-driven synchronization.

_Sources:_ [GeoServer REST docs](https://docs.geoserver.org/stable/en/user/rest/index.html), [GeoServer REST API details](https://geoserver.org/geoserver/en/user/rest/api/details/), [GeoServer layers REST docs](https://geoserver.org/geoserver/en/user/rest/api/layers/), [MCP server concepts](https://modelcontextprotocol.io/docs/learn/server-concepts)

### Communication Protocols

There are two independent protocol axes:

- **Client to GeoServer MCP:** MCP transport.
- **GeoServer MCP to GeoServer:** HTTP/HTTPS REST and OGC service requests.

For the MCP transport, Dockerized operation points toward **Streamable HTTP** as the primary runtime transport because the server operates as an independent container process and can be reached over a network endpoint. The MCP transport specification describes Streamable HTTP as allowing an independent server process that can handle multiple client connections. The Python SDK README also shows `mcp.run(transport="streamable-http")`.

However, client compatibility can vary. Architecture should consider supporting both:

- Streamable HTTP for Dockerized server operation.
- stdio for local development and clients that still prefer process-managed MCP servers.

For GeoServer integration, use HTTP/HTTPS only. GeoServer REST requires authentication by default and uses Basic authentication unless changed by GeoServer security configuration. OGC services expose capabilities over HTTP/HTTPS and are separate from the REST configuration API. GeoServer virtual services also mean capabilities can exist at global, workspace, or layer service URLs, so URL construction must be explicit and testable.

_HTTP/HTTPS Protocols:_ Required for GeoServer REST and OGC service requests. Basic auth is the v1 credential model.

_WebSocket Protocols:_ Not required.

_Message Queue Protocols:_ Not required for v1.

_gRPC and Protocol Buffers:_ Not required.

_Sources:_ [MCP transports specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports), [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk), [GeoServer REST API details](https://geoserver.org/geoserver/en/user/rest/api/details/), [GeoServer virtual services](https://docs.geoserver.org/main/en/user/configuration/virtual-services/)

### Data Formats and Standards

GeoServer MCP must handle JSON, XML, and OGC capabilities documents.

Recommended rules:

- Prefer GeoServer REST JSON where stable and sufficient.
- Use XML when GeoServer endpoints provide richer or more consistent data.
- Parse OGC capabilities as XML with service-specific parsers.
- Normalize both REST and OGC data into internal typed models before exposing MCP responses.
- Preserve source evidence metadata in each response: source type, URL/path, status, timestamp, and parse status.

OGC capability documents should not be treated as generic XML blobs. WMS, WFS, WCS, and WMTS have different concepts and version-specific differences. The v1 implementation should define a minimal normalized `ServiceCapability` model and retain raw-ish service-specific fields only where they are needed for diagnostics.

Data Directory inspection also uses XML configuration files, but GeoServer documentation warns that direct data directory configuration-file access is not the preferred programmatic management path; REST should be used for programmatic access. Therefore filesystem parsing should be evidence enrichment only, not the canonical control plane.

_JSON and XML:_ Both are required. JSON is useful for GeoServer REST responses. XML is required for OGC capabilities and Data Directory evidence.

_Protobuf and MessagePack:_ Not required.

_CSV and Flat Files:_ Not required except possibly exported reports in future.

_Custom Data Formats:_ OGC service-specific XML capabilities are the important domain-specific formats.

_Sources:_ [GeoServer REST docs](https://docs.geoserver.org/stable/en/user/rest/index.html), [GeoServer WMS reference](https://docs.geoserver.org/latest/en/user/services/wms/reference/), [GeoServer WFS reference](https://geoserver.org/geoserver/en/user/services/wfs/reference/), [GeoServer data directory structure](https://docs.geoserver.org/latest/en/user/datadirectory/structure.html)

### System Interoperability Approaches

GeoServer MCP should act as an **anti-corruption layer** between AI agents and GeoServer deployments. The agent should see stable concepts such as `GeoServerInstance`, `CatalogResource`, `ServiceCapability`, and `DiagnosticFinding`, while the server absorbs differences in REST endpoints, capabilities documents, HTTP failures, authentication failures, and optional data-directory availability.

Recommended interoperability pattern:

- One configured `GeoServerInstance` owns REST base URL, OGC base URL behavior, auth reference, timeout policy, and optional Data Directory path.
- Each inspection operation produces typed evidence.
- Evidence is normalized into inventory models.
- Diagnostic rules run over normalized models and evidence metadata.
- MCP responses return both user-facing summaries and machine-readable structures.

This pattern is more resilient than direct point-to-point endpoint mirroring because GeoServer deployments vary. Virtual services are especially important: global OGC service URLs and workspace/layer virtual service URLs can expose different capabilities. The integration model should represent this instead of assuming one capabilities document tells the whole truth.

_Point-to-Point Integration:_ GeoServer MCP uses direct HTTP/HTTPS calls to each configured GeoServer Instance.

_API Gateway Patterns:_ Not needed internally. GeoServer MCP itself is the gateway/adapter for AI agents.

_Service Mesh:_ Not relevant to v1.

_Enterprise Service Bus:_ Not relevant.

_Sources:_ [GeoServer virtual services](https://docs.geoserver.org/main/en/user/configuration/virtual-services/), [GeoServer services docs](https://docs.geoserver.org/main/en/user/services/index.html), [GeoServer catalogue API](https://geoserver.org/geoserver/en/developer/programming-guide/config/catalog/), [MCP server concepts](https://modelcontextprotocol.io/docs/learn/server-concepts)

### Microservices Integration Patterns

GeoServer MCP should be a single-process modular service in v1, not a microservice suite. The Dockerized server should remain stateless except for loaded configuration and optional in-memory caching. Multi-instance behavior should be modeled as routing within the application, not as separate containers per GeoServer instance.

Useful microservice-derived patterns:

- **Circuit breaker / failure isolation:** one failing GeoServer Instance must not block others.
- **Timeout budgets:** each GeoServer request should have explicit timeout behavior.
- **Bulkhead behavior:** inspection should isolate per-instance failures and report partial results.
- **Typed error taxonomy:** failures become structured reason codes, not generic exceptions.

Not recommended for v1:

- Service discovery system.
- Message bus.
- Distributed workers.
- Saga/transaction patterns.

_API Gateway Pattern:_ The MCP server acts as the agent-facing API gateway for GeoServer operations.

_Service Discovery:_ Static config file/env configuration is enough for v1.

_Circuit Breaker Pattern:_ Useful conceptually for repeated failing instances, but start with per-call timeouts and error isolation before adding stateful circuit-breaker behavior.

_Saga Pattern:_ Not relevant in read-only v1.

_Sources:_ [MCP transports specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports), [GeoServer REST API details](https://geoserver.org/geoserver/en/user/rest/api/details/), [GeoServer status docs](https://geoserver.org/geoserver/en/user/configuration/status/)

### Event-Driven Integration

Event-driven architecture is not needed for v1. The product's first workflow is user/agent-initiated inspection and diagnostics. Adding polling, scheduling, event capture, or message brokers would add operational complexity before the core read-only model is proven.

Future event-driven use cases may become valid:

- Scheduled inventory snapshots.
- Drift detection between environments.
- Usage-statistics harvesting from monitoring extension data.
- Alerting on broken services or unavailable instances.

These should be v2+ concerns and should only be designed after v1 establishes stable inventory models and diagnostic findings.

_Publish-Subscribe Patterns:_ Not recommended for v1.

_Event Sourcing:_ Not recommended for v1.

_Message Broker Patterns:_ Not recommended for v1.

_CQRS Patterns:_ The read-only v1 is effectively query-side only; do not formalize CQRS until write/admin operations exist.

_Sources:_ [GeoServer monitoring extension](https://docs.geoserver.org/main/en/user/extensions/monitoring/), [GeoServer monitoring overview](https://docs.geoserver.org/main/en/user/extensions/monitoring/overview/)

### Integration Security Patterns

Security integration must be conservative because GeoServer MCP will hold administrator-equivalent credentials while exposing capabilities to AI agents.

Required v1 security patterns:

- Credentials supplied by environment variables or secret stores, not embedded in reports.
- Config file references secret names rather than literal passwords where possible.
- Basic auth over HTTPS should be the expected production posture.
- Redaction must apply to credentials, store connection strings, JDBC URLs, passwords, tokens, and sensitive host details when configured.
- Read-only enforcement must happen in code by not implementing mutation operations and by rejecting mutation-style requests.
- Optional Data Directory mounts should be read-only Docker mounts.
- Filesystem inspection must stay inside configured paths and never expose arbitrary host filesystem content.

MCP-specific security matters because tools expose real system capabilities to AI clients. Use narrow, named, task-specific tools instead of a generic `http_request` tool or arbitrary file reader. This reduces prompt-injection and tool-misuse blast radius.

_OAuth 2.0 and JWT:_ Not v1; basic auth is the chosen initial model.

_API Key Management:_ Not v1 unless environment secret references are treated as API-key-like values.

_Mutual TLS:_ Future enterprise option, not v1.

_Data Encryption:_ HTTPS is expected for GeoServer connections in production; Docker/runtime secret storage is deployment-specific.

_Sources:_ [GeoServer REST API details](https://geoserver.org/geoserver/en/user/rest/api/details/), [MCP roots security considerations](https://modelcontextprotocol.io/docs/concepts/roots), [MCP server concepts](https://modelcontextprotocol.io/docs/learn/server-concepts), [MCP transports specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)

### Integration Pattern Recommendation

Recommended v1 integration architecture:

- Python MCP server using the official Python SDK.
- Primary MCP transport: Streamable HTTP for Dockerized use; optional stdio for local development/client compatibility.
- GeoServer integration: authenticated HTTP/HTTPS client with GET-only REST and OGC capabilities requests.
- Internal model: normalize REST, OGC, and optional Data Directory evidence into typed inventory and diagnostic models.
- Tool design: expose task-level MCP tools, not raw GeoServer endpoint tools.
- Data Directory: optional read-only evidence adapter, never required.
- Failure model: structured reason codes for network, auth, authorization, unsupported endpoint, parse failure, unavailable extension, missing data directory, and partial result.
- Security model: no generic HTTP proxy, no mutation tools, no arbitrary filesystem tools, strict redaction.

## Architectural Patterns and Design

### System Architecture Patterns

The best v1 architecture is a **modular monolith with hexagonal boundaries**. The product should run as one Dockerized Python process, but internally it should separate domain logic from adapters. This gives the project low operational complexity while preserving clean boundaries for future write/admin capabilities.

Recommended module boundaries:

- **MCP interface adapter:** registers tools, resources, prompts, transport, and request/response conversion.
- **Application services:** inventory orchestration, diagnostics orchestration, comparison, report generation.
- **Domain models:** `GeoServerInstance`, `CatalogResource`, `ServiceCapability`, `Evidence`, `DiagnosticFinding`, `InspectionResult`.
- **GeoServer REST adapter:** GET-only authenticated REST client.
- **OGC capabilities adapter:** WMS/WFS/WCS/WMTS capabilities fetch and parse.
- **Data Directory adapter:** optional read-only filesystem evidence.
- **Config/secrets adapter:** config file, environment variables, secret-file support.
- **Redaction and safety layer:** centralized output scrubber and mutation guard.

This avoids two poor alternatives:

- A raw endpoint wrapper, which leaks GeoServer's API complexity directly into MCP.
- A microservice architecture, which adds deployment complexity before the product has stable domain contracts.

The GeoServer docs support REST as the programmatic configuration interface, while the data-directory docs warn that direct config-file access is not a complete reference and should not be the primary programmatic path. That supports making REST/OGC the primary evidence path and Data Directory inspection a secondary adapter.

_Source:_ [GeoServer REST docs](https://docs.geoserver.org/stable/en/user/rest/index.html), [GeoServer data directory structure](https://geoserver.org/geoserver/en/user/datadirectory/structure/), [GeoServer catalogue API](https://geoserver.org/geoserver/en/developer/programming-guide/config/catalog/), [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

### Design Principles and Best Practices

Core design principles for GeoServer MCP:

- **Contract-first MCP surface:** define stable tool/resource names and response schemas before implementation.
- **Evidence-first diagnostics:** every finding should cite source type, instance, endpoint/path, status, and parse result.
- **Read-only by construction:** do not implement generic REST callers or mutation-capable clients in v1.
- **Normalize before exposing:** parse GeoServer REST/OGC/Data Directory evidence into internal models before returning MCP output.
- **Partial success is normal:** multi-instance operations should return per-instance status, not fail all-or-nothing.
- **Explicit uncertainty:** unknown and unavailable information are first-class result states.
- **Centralized redaction:** all output paths pass through secret/sensitive-value redaction.

The architecture should prefer domain-specific operations over generic pass-through tools. MCP docs frame tools as model-requested actions and resources as contextual data; for this product, tools should perform bounded read-only tasks and resources can expose stable inventory/report views where client support is useful.

_Source:_ [MCP server concepts](https://modelcontextprotocol.io/docs/learn/server-concepts), [GeoServer REST API details](https://geoserver.org/geoserver/en/user/rest/api/details/), [GeoServer virtual services](https://docs.geoserver.org/main/en/user/configuration/virtual-services/)

### Scalability and Performance Patterns

The main scaling problem is not CPU; it is coordinated inspection of multiple slow or inconsistent GeoServer endpoints. Architectural patterns should focus on latency isolation and bounded concurrency.

Recommended v1 patterns:

- **Bounded async concurrency:** inspect multiple instances concurrently, but cap per-server and total outbound requests.
- **Timeout budget:** each tool invocation has a total budget and per-request timeouts.
- **Request-scoped cache:** avoid fetching the same endpoint repeatedly inside one inventory/report run.
- **Per-instance isolation:** one unreachable instance produces a finding and does not block other instances.
- **Large response handling:** OGC capabilities documents can be large; parsers should avoid unnecessary raw response echoing.
- **Progressive detail:** list tools return summaries; detail tools fetch deeper metadata on demand.

Avoid persistent caching until a concrete use case exists. Durable snapshots and drift detection can be added later, but v1 should keep runtime state simple.

Recent MCP production-pattern research highlights timeouts, structured errors, observability, and server contracts as important production dimensions. Even if that research is not an implementation standard, it matches the design needs here: machine-readable failure semantics and explicit timeout behavior are core to an AI-agent-facing diagnostic tool.

_Source:_ [MCP transports specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports), [Bridging Protocol and Production](https://arxiv.org/abs/2603.13417), [GeoServer WMS reference](https://docs.geoserver.org/latest/en/user/services/wms/reference/)

### Integration and Communication Patterns

The architectural communication pattern should be **hub-and-spoke inspection**:

- MCP client talks to GeoServer MCP.
- GeoServer MCP talks to each configured GeoServer Instance.
- GeoServer MCP optionally reads configured local Data Directory mounts.
- GeoServer MCP returns normalized inventory, diagnostics, and reports.

There should be no direct client-to-GeoServer credential delegation through MCP. The server owns configured credential use and redaction.

Transport recommendation:

- **Primary:** Streamable HTTP for Dockerized operation.
- **Secondary:** stdio for local development and clients that prefer launching a local process.

GeoServer endpoint strategy:

- Use REST for catalog and service configuration inventory.
- Use OGC capabilities for advertised service visibility.
- Recognize global and virtual service URLs because workspace and layer virtual services can expose subsets of capabilities.
- Treat system status endpoints as optional diagnostics inputs when available.

_Source:_ [MCP transports specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports), [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk), [GeoServer virtual services](https://docs.geoserver.org/main/en/user/configuration/virtual-services/), [GeoServer status docs](https://geoserver.org/geoserver/en/user/configuration/status/)

### Security Architecture Patterns

GeoServer MCP has a high-trust position because it holds administrator-equivalent GeoServer credentials. The security architecture should assume that tool misuse and prompt injection are realistic risks, even in a read-only v1.

Required patterns:

- **No generic HTTP tool:** never expose arbitrary URL fetch or raw GeoServer REST invocation.
- **Allowlisted instance targets:** outbound requests only go to configured GeoServer Instance base URLs and derived service URLs.
- **Disable/limit redirects:** avoid redirect-based SSRF bypasses unless explicitly validated.
- **Read-only client methods:** implement GET-only REST client methods in v1.
- **Secret indirection:** config references environment variables or secret files instead of storing passwords inline.
- **Redaction registry:** known credentials, credential fields, JDBC URLs, connection parameters, and configured sensitive keys are scrubbed.
- **Read-only Data Directory mounts:** Docker mounts should be read-only, and file reads must stay under configured paths.
- **Safe XML parsing:** disable external entity resolution and network access during XML parsing.

OWASP SSRF guidance emphasizes allowlisting and redirect concerns for server-side HTTP clients. OWASP XXE guidance reinforces safe XML parser configuration. These matter here because the server fetches URLs and parses XML from GeoServer/OGC endpoints.

_Source:_ [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html), [OWASP XXE Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html), [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html), [MCP roots security considerations](https://modelcontextprotocol.io/docs/concepts/roots), [GeoServer REST API details](https://geoserver.org/geoserver/en/user/rest/api/details/)

### Data Architecture Patterns

Use an internal **evidence-to-model pipeline**:

1. Fetch evidence from REST, OGC, or Data Directory.
2. Parse evidence into source-specific records.
3. Normalize records into domain models.
4. Run diagnostics over normalized models plus evidence metadata.
5. Return MCP response DTOs with findings, inventory, and unavailable-information details.

Key domain model recommendations:

- `Evidence`: source type, instance, URL/path, timestamp, status, raw format, parser status.
- `InspectionStatus`: success, partial, unavailable, failed.
- `ReasonCode`: network_error, auth_failed, forbidden, not_found, unsupported_endpoint, disabled_service, parse_error, missing_data_directory, unreadable_data_directory, redacted, unknown.
- `CatalogResource`: kind, name, workspace, store, enabled/advertised flags, style relationships, source evidence.
- `ServiceCapability`: service, version, scope, advertised resources, operations, source evidence.
- `DiagnosticFinding`: severity, reason code, affected resource, evidence, explanation, suggested next step.

Do not store raw GeoServer responses as durable product data in v1. Return concise normalized responses and optionally include source metadata. Large raw XML or JSON should be accessible only through explicit debug/developer workflows, if at all.

_Source:_ [GeoServer REST docs](https://docs.geoserver.org/stable/en/user/rest/index.html), [GeoServer catalogue API](https://geoserver.org/geoserver/en/developer/programming-guide/config/catalog/), [GeoServer data directory structure](https://geoserver.org/geoserver/en/user/datadirectory/structure/), [MCP server concepts](https://modelcontextprotocol.io/docs/learn/server-concepts)

### Deployment and Operations Architecture

The Dockerized runtime should be simple and auditable:

- One container image.
- One default command for Streamable HTTP.
- Config mounted read-only.
- Optional Data Directory mounts read-only.
- Credentials via environment variables and later Docker secrets/secret files.
- Health/startup validation for config syntax and duplicate instance names.
- Runtime tool-level status for GeoServer reachability instead of requiring every instance to be reachable at container startup.

Do not bake secrets, sample credentials, or mutable local data into the image. Docker's own secrets documentation and broader security guidance support using runtime secret injection rather than hardcoding credentials.

Testing architecture should use three tiers:

- **Unit tests:** config, redaction, schemas, parsers, diagnostics rules.
- **HTTP contract tests:** mocked GeoServer REST/OGC responses for error taxonomy and version differences.
- **Docker integration tests:** real GeoServer containers, optional PostGIS, mounted/unmounted Data Directory cases, authentication failure cases.

The official GeoServer Docker repository documents official image usage from `docker.osgeo.org/geoserver:<VERSION>`, making it a suitable source for integration fixtures when licensing and runtime constraints are acceptable.

_Source:_ [GeoServer Docker repository](https://github.com/geoserver/docker), [Docker secrets docs](https://docs.docker.com/engine/swarm/secrets/), [Pydantic settings docs](https://pydantic.dev/docs/validation/1.10/usage/settings/), [Docker Testcontainers Python guide](https://docs.docker.com/guides/testcontainers-python-getting-started/run-tests/), [pytest docs](https://docs.pytest.org/en/stable/contents.html)

### Architectural Recommendation

Recommended architecture for v1:

- Python modular monolith in one Dockerized process.
- Official Python MCP SDK with Streamable HTTP primary transport and optional stdio.
- Hexagonal architecture: MCP, GeoServer REST, OGC, Data Directory, config/secrets, and reporting as adapters.
- Internal domain model centered on evidence, inventory, service capabilities, and diagnostic findings.
- REST/OGC as primary evidence; Data Directory as optional read-only enrichment.
- Read-only by construction: no generic REST proxy, no mutation endpoint wrappers, no arbitrary filesystem reader.
- Bounded concurrent inspection, timeout budgets, request-scoped cache, and per-instance partial-result reporting.
- Security baseline: allowlisted configured targets, safe XML parsing, secret redaction, read-only mounts, and explicit unsupported responses for mutation requests.

## Implementation Approaches and Technology Adoption

### Technology Adoption Strategies

Adopt the stack incrementally by building a thin vertical slice before filling the entire GeoServer surface. The first slice should prove Docker startup, config loading, one GeoServer connection check, one inventory endpoint, one OGC capabilities parse, one diagnostic finding, and one MCP tool response.

Recommended adoption sequence:

1. **Foundation:** Python package, Dockerfile, config model, logging, redaction, MCP startup.
2. **Connection slice:** one configured instance, basic auth, `/rest/about/version` or equivalent metadata probe, structured error taxonomy.
3. **Inventory slice:** workspaces, stores, layers, styles via GET-only REST.
4. **Capabilities slice:** WMS and WFS capabilities parsing first; WCS and WMTS next.
5. **Diagnostics slice:** unreachable, auth failed, forbidden, parse failure, missing data directory, disabled/unavailable service.
6. **Multi-instance slice:** fan-out inspection with partial results and comparison.
7. **Report slice:** consolidated markdown/JSON-style operational report exposed through MCP.

Do not start by generating a large tool catalog. Start with stable task-level tools and add coverage behind those tools.

_Source:_ [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk), [GeoServer REST docs](https://docs.geoserver.org/stable/en/user/rest/index.html), [GeoServer Docker install docs](https://docs.geoserver.org/stable/en/user/installation/docker.html)

### Development Workflows and Tooling

Recommended Python project tooling:

- `pyproject.toml` as the canonical project file.
- Python 3.12+ unless the MCP SDK or dependency constraints require a lower floor.
- `uv` for fast local dependency management, with standard `pip` compatibility preserved by `pyproject.toml`.
- `ruff` for lint/format, `mypy` or pyright for type checking, and `pytest` for tests.
- `httpx.AsyncClient` for outbound GeoServer calls.
- Pydantic settings for config/env/secrets loading.
- Official Python MCP SDK / FastMCP for MCP server implementation.

HTTPX is a good fit because it supports both sync and async APIs, defaults to timeouts, and exposes detailed timeout categories. Use one scoped `AsyncClient` rather than creating clients in hot loops, because HTTPX docs explicitly warn that connection pooling benefits depend on client reuse.

Pydantic settings is appropriate because it supports environment variables and secret-file sources, which map directly to Dockerized deployment patterns.

_Source:_ [HTTPX async support](https://www.python-httpx.org/async/), [HTTPX timeouts](https://www.python-httpx.org/advanced/timeouts/), [Pydantic settings](https://pydantic.dev/docs/validation/dev/api/pydantic_settings/), [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

### Testing and Quality Assurance

Testing should be designed around the PRD's risk areas: multi-instance behavior, partial access, XML parsing, redaction, and read-only safety.

Recommended test layers:

- **Unit tests:** config parsing, secret resolution, redaction, reason-code mapping, safe URL construction, safe path checks, diagnostics rules.
- **Parser tests:** fixture-based REST JSON/XML and OGC capabilities samples for WMS, WFS, WCS, and WMTS.
- **HTTP contract tests:** mock GeoServer responses with `respx` for `httpx`, covering 200, 401, 403, 404, 5xx, timeouts, malformed XML, and unsupported endpoints.
- **MCP contract tests:** inspect registered tools/resources/prompts and validate response schema stability.
- **Docker integration tests:** run against official GeoServer Docker images, with at least one instance reachable, one auth failure scenario, and one optional Data Directory mount scenario.
- **Regression fixtures:** keep small recorded/sample responses for known GeoServer versions and capability variants.

Pytest supports parametrized tests and fixtures, which is useful for testing the same diagnostics across multiple GeoServer versions, service types, and failure modes. RESPX provides a pytest fixture/decorator for mocking HTTPX. Docker/Testcontainers-style tests let integration tests use real services rather than only mocks.

Acceptance criteria before architecture/epics should include a minimal compatibility matrix:

- One current stable GeoServer image.
- One older supported GeoServer version [ASSUMPTION: exact older version selected during architecture].
- REST JSON/XML variant coverage where endpoints support both.
- WMS and WFS capabilities at minimum.
- Data Directory unavailable and available cases.

_Source:_ [pytest parametrization](https://pytest.org/en/8.1.x/parametrize.html), [pytest fixtures](https://pytest.org/en/6.2.x/fixture.html), [RESPX guide](https://lundberg.github.io/respx/guide/), [Testcontainers for Python](https://docs.docker.com/guides/testcontainers-python-getting-started/), [GeoServer testing docs](https://docs.geoserver.org/main/en/developer/programming-guide/testing/), [GeoServer Docker install docs](https://docs.geoserver.org/stable/en/user/installation/docker.html)

### Deployment and Operations Practices

Recommended Docker runtime:

- Image exposes a Streamable HTTP endpoint by default.
- Config file mounted read-only, for example `/config/geoserver-mcp.yaml`.
- Optional Data Directory mounts read-only under a dedicated base such as `/geoserver-data/<instance-name>`.
- Secrets supplied by environment variables or secret files.
- Container logs are structured enough to distinguish startup, config validation, GeoServer request failure, parser failure, and redaction/safety events.
- Health endpoint or MCP status tool verifies process health; GeoServer reachability is tool-level status rather than hard startup dependency.

Recommended compose development stack:

- `geoserver-mcp` service.
- One or more `geoserver` services using official GeoServer images.
- Optional `postgis` service for store-related fixture data.
- Mounted sample config and optional mounted data directory.
- Explicit version tags; no `latest` tags.

Operationally, default credentials in test fixtures must be treated as test-only. The official GeoServer Docker docs and repository emphasize configuring credentials; the MCP project should not normalize default admin credentials for production examples.

_Source:_ [GeoServer Docker install docs](https://docs.geoserver.org/stable/en/user/installation/docker.html), [GeoServer Docker repository](https://github.com/geoserver/docker), [Docker secrets docs](https://docs.docker.com/engine/swarm/secrets/)

### Team Organization and Skills

For a solo developer, the implementation should be split into narrow story-sized increments that produce working vertical slices. Required skill areas:

- Python async programming.
- MCP server concepts: tools, resources, prompts, transports.
- GeoServer REST and OGC capabilities.
- XML parsing and XML security.
- Docker and Docker Compose.
- Test design for HTTP clients and containerized services.
- Operational security basics: secrets, redaction, SSRF prevention, read-only filesystem boundaries.

The highest-risk skill gaps are not basic Python coding; they are GeoServer semantic normalization and secure agent-facing tool design. Architecture should define response contracts and diagnostic taxonomy before broad endpoint coverage begins.

_Source:_ [MCP server concepts](https://modelcontextprotocol.io/docs/learn/server-concepts), [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html), [OWASP XXE Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html)

### Cost Optimization and Resource Management

Keep v1 operationally cheap:

- No database.
- No message broker.
- No Kubernetes requirement.
- No scheduled background workers.
- Request-scoped caching only.
- Bounded concurrency and explicit timeout defaults.
- Compact responses by default, with detail tools for deeper inspection.

This lowers contributor and operator burden. The main runtime costs are outbound GeoServer calls and parsing large capabilities documents. Those are controlled through timeout budgets, concurrency limits, and summary/detail separation.

_Source:_ [HTTPX timeouts](https://www.python-httpx.org/advanced/timeouts/), [MCP transports specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)

### Risk Assessment and Mitigation

Primary risks and mitigations:

- **SDK churn:** Pin official MCP SDK versions; isolate MCP adapter from domain logic.
- **GeoServer version differences:** Capability-detect endpoints; maintain fixture samples and integration tests for selected versions.
- **Over-broad MCP surface:** Use task-level tools; reject generic HTTP proxy design.
- **Credential leakage:** Central redaction layer; schema-level sensitive fields; tests for output/log redaction.
- **SSRF/tool misuse:** Only allow configured instance base URLs; validate derived URLs; disable or strictly validate redirects.
- **XXE/XML parser risk:** Safe parser defaults; disable entity/network resolution.
- **False diagnostics:** Every finding includes evidence and confidence/source metadata; unknowns remain explicit.
- **Data Directory assumptions:** Treat filesystem access as optional; mount read-only; fail softly.
- **Slow large deployments:** Bounded concurrency, timeouts, request-scoped caching, summary/detail split.

_Source:_ [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html), [OWASP XXE Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html), [HTTPX timeouts](https://www.python-httpx.org/advanced/timeouts/), [GeoServer data directory structure](https://geoserver.org/geoserver/en/user/datadirectory/structure/)

## Technical Research Recommendations

### Implementation Roadmap

Recommended first implementation roadmap:

1. Scaffold Python package, Dockerfile, config model, logging, tests, and MCP startup.
2. Implement config/env/secrets loading and validation for multiple instances.
3. Implement safe GeoServer HTTP client with basic auth, allowlisted base URLs, timeouts, redirects disabled by default, and structured errors.
4. Implement `check_instances` MCP tool.
5. Implement REST inventory for workspaces, stores, layers/layer groups, and styles.
6. Implement OGC capabilities inspection for WMS and WFS first, then WCS and WMTS.
7. Implement diagnostic finding model and first reason-code taxonomy.
8. Implement compare/report tools and partial-access reporting.
9. Add optional Data Directory status and one minimal Data Directory-derived diagnostic.
10. Build Docker Compose integration fixture with official GeoServer image and optional PostGIS.

### Technology Stack Recommendations

- Language: Python.
- MCP: official Python MCP SDK / FastMCP.
- HTTP: `httpx.AsyncClient`.
- Config: Pydantic settings or equivalent typed settings layer.
- XML: `lxml` or stdlib XML with explicit safe parser configuration; choose one during architecture.
- Testing: `pytest`, `respx`, Docker Compose or Testcontainers-style integration tests.
- Docker: pinned Python base image and pinned GeoServer fixture image.
- No database, no broker, no Kubernetes requirement for v1.

### Skill Development Requirements

- MCP Python SDK usage and transport behavior.
- GeoServer REST endpoint coverage and status semantics.
- OGC capabilities parsing for WMS/WFS/WCS/WMTS.
- Secure XML parsing.
- Dockerized Python service packaging.
- Pytest fixture and parametrization patterns.
- Secret redaction and SSRF-safe HTTP client design.

### Success Metrics and KPIs

- A Dockerized server starts with mounted config and environment-provided credentials.
- `check_instances` distinguishes network, auth, forbidden, unsupported endpoint, parse, and partial-result failures.
- Inventory tools work against at least two configured GeoServer instances.
- WMS and WFS capabilities parse successfully from fixture GeoServer instances.
- Output redaction tests prove credentials and sensitive store connection details are not returned.
- One real GeoServer integration test suite runs locally through Docker.
- No v1 tool invokes GeoServer mutation methods.

# Dockerized GeoServer MCP Server: Comprehensive Technical Research

## Executive Summary

GeoServer MCP should be built as a Dockerized Python MCP server that gives AI agents safe, read-only operational access to multiple GeoServer instances. The strongest architecture is a Python modular monolith with hexagonal boundaries: MCP transport at the edge, GeoServer REST and OGC capabilities adapters for primary evidence, an optional read-only Data Directory adapter for enrichment, and internal domain models for inventory, capabilities, evidence, and diagnostic findings.

The research rejects a raw GeoServer REST wrapper as the wrong abstraction. A useful MCP server should expose task-level operations such as connection checks, catalog inventory, service capability inspection, comparison, diagnostics, and report generation. This keeps the agent-facing contract stable while hiding GeoServer version differences, endpoint variations, OGC XML details, and partial-access failures.

The v1 implementation should stay deliberately narrow: Dockerized Python server, official Python MCP SDK, basic auth, config file plus environment variables, HTTP/HTTPS GET-only GeoServer access, WMS/WFS first for OGC capabilities, structured reason codes, strict redaction, and Docker-based integration fixtures. CRUD/admin actions, usage statistics, persistent storage, brokers, Kubernetes-specific behavior, and broad extension management should remain future work.

**Key Technical Findings:**

- Python is the preferred implementation language because the project is diagnostics-heavy, XML/OGC-heavy, filesystem-aware, and operationally oriented.
- The official Python MCP SDK / FastMCP is sufficient for v1, with Streamable HTTP as the Dockerized transport and optional stdio for development/client compatibility.
- GeoServer REST should be used for catalog and service configuration inventory, while OGC capabilities should be parsed separately for advertised service visibility.
- Data Directory inspection should be optional read-only evidence, not the primary programmatic control plane.
- The internal architecture should normalize REST, OGC, and filesystem evidence into stable models before exposing MCP responses.
- Security must be built in from the start: no generic HTTP proxy, no mutation tools, no arbitrary filesystem reader, strict target allowlisting, safe XML parsing, and centralized redaction.

**Technical Recommendations:**

- Build a Python modular monolith using the official Python MCP SDK.
- Use a hexagonal architecture with adapters for MCP, GeoServer REST, OGC capabilities, optional Data Directory, config/secrets, and reporting.
- Expose task-level MCP tools instead of one tool per GeoServer endpoint.
- Implement a structured diagnostic taxonomy early and treat partial access as a normal result state.
- Use Docker Compose/Testcontainers-style fixtures with official GeoServer images for integration testing.

## Table of Contents

1. Technical Research Introduction and Methodology
2. Technical Landscape and Architecture Analysis
3. Implementation Approaches and Best Practices
4. Technology Stack Evolution and Current Trends
5. Integration and Interoperability Patterns
6. Performance and Scalability Analysis
7. Security and Compliance Considerations
8. Strategic Technical Recommendations
9. Implementation Roadmap and Risk Assessment
10. Future Technical Outlook and Innovation Opportunities
11. Technical Research Methodology and Source Verification
12. Technical Appendices and Reference Materials

## 1. Technical Research Introduction and Methodology

### Technical Research Significance

GeoServer is a mature GIS server with broad REST, OGC, extension, and filesystem-backed configuration surfaces. MCP is a rapidly evolving standard for giving AI agents structured access to tools, context, and external systems. Combining them is useful only if the MCP server is safer and more meaningful than generic HTTP access.

The technical challenge is to bridge GeoServer's operational model into an agent-safe interface: multi-instance inventory, version-aware inspection, OGC capabilities parsing, optional filesystem evidence, and diagnostics that can explain what was inspected and what was unavailable.

_Technical Importance:_ The project creates an AI-agent operational interface for GeoServer estates without exposing broad mutation surfaces.

_Business Impact:_ Open-source GIS and IT professionals can reduce manual GeoServer inspection work and create a foundation for future safe admin automation.

_Source:_ [MCP server concepts](https://modelcontextprotocol.io/docs/learn/server-concepts), [GeoServer REST docs](https://docs.geoserver.org/stable/en/user/rest/index.html), [GeoServer Docker install docs](https://docs.geoserver.org/stable/en/user/installation/docker.html)

### Technical Research Methodology

- **Technical Scope:** MCP SDK/runtime choice, GeoServer REST/OGC integration, Dockerized deployment, multi-instance config, optional Data Directory inspection, diagnostics, security, testing, and implementation roadmap.
- **Data Sources:** Official MCP docs/specs, official MCP SDK repositories, GeoServer user/developer docs, GeoServer Docker docs, OWASP security guidance, and current implementation/tooling docs.
- **Analysis Framework:** Compare implementation options by v1 safety, Docker suitability, GIS/OGC fit, testability, contributor ergonomics, and future write/admin extensibility.
- **Time Period:** Current as of 2026-05-27.
- **Technical Depth:** Decision-ready guidance for BMAD architecture, not low-level implementation code.

### Technical Research Goals and Objectives

**Original Technical Goals:** Research architecture options for a Dockerized GeoServer MCP server based on the PRD. Focus on TypeScript vs Python MCP SDK, GeoServer REST/OGC API coverage, multi-instance config, diagnostics taxonomy, optional data-directory inspection, and testing strategy.

**Achieved Technical Objectives:**

- Selected Python as the recommended implementation language.
- Recommended the official Python MCP SDK / FastMCP.
- Defined REST/OGC/Data Directory evidence-source roles.
- Recommended modular monolith and hexagonal boundaries.
- Proposed a v1 diagnostic taxonomy and failure model.
- Proposed Dockerized deployment and integration-test strategy.

## 2. Technical Landscape and Architecture Analysis

### Current Technical Architecture Patterns

The recommended architecture is a Dockerized Python modular monolith. It should be internally modular but operationally simple: one process, one container image, one MCP server, and adapters around external systems.

_Dominant Patterns:_ Modular monolith, hexagonal architecture, adapter pattern, evidence-to-model pipeline, task-level MCP tools.

_Architectural Evolution:_ Start with read-only inspection and diagnostics. Add write/admin operations only after evidence, redaction, diagnostic, and confirmation patterns are stable.

_Architectural Trade-offs:_ A modular monolith gives much lower operational overhead than microservices while keeping enough boundaries for future extension.

_Source:_ [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk), [MCP transports](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports), [GeoServer REST docs](https://docs.geoserver.org/stable/en/user/rest/index.html)

### System Design Principles and Best Practices

Core principles:

- Normalize before exposing.
- Keep tools task-level and bounded.
- Treat partial access as normal.
- Make all diagnostics evidence-backed.
- Keep v1 read-only by construction.
- Centralize redaction.
- Make Data Directory access optional.

_Design Principles:_ Contract-first MCP surface, explicit domain models, per-instance isolation, and no generic pass-through tools.

_Best Practice Patterns:_ Adapter boundaries, typed settings, request-scoped cache, structured errors, safe XML parser configuration, and Dockerized integration fixtures.

_Architectural Quality Attributes:_ Maintainability, security, reliability under partial failure, explainability of diagnostic findings, and future extensibility.

_Source:_ [MCP server concepts](https://modelcontextprotocol.io/docs/learn/server-concepts), [GeoServer REST API details](https://geoserver.org/geoserver/en/user/rest/api/details/), [GeoServer data directory structure](https://geoserver.org/geoserver/en/user/datadirectory/structure/)

## 3. Implementation Approaches and Best Practices

### Current Implementation Methodologies

Implementation should proceed through vertical slices rather than broad endpoint coverage. The first useful slice is: Docker startup, config loading, one GeoServer connection check, one structured MCP tool response, and tests.

_Development Approaches:_ Vertical slices, test-first diagnostics rules, explicit response schemas, and fixture-backed integration tests.

_Code Organization Patterns:_ MCP adapter, application services, domain models, GeoServer REST adapter, OGC adapter, Data Directory adapter, config/secrets, redaction, reports.

_Quality Assurance Practices:_ Unit tests, HTTP mocks, parser fixtures, Docker integration tests, MCP contract checks, redaction tests, and mutation-safety tests.

_Deployment Strategies:_ Docker image with mounted config, env/secrets for credentials, optional read-only Data Directory mounts, and no hard dependency on GeoServer reachability at startup.

_Source:_ [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk), [pytest docs](https://pytest.org/en/stable/), [RESPX guide](https://lundberg.github.io/respx/guide/), [GeoServer Docker install docs](https://docs.geoserver.org/stable/en/user/installation/docker.html)

### Implementation Framework and Tooling

_Development Frameworks:_ Official Python MCP SDK / FastMCP.

_Tool Ecosystem:_ `httpx.AsyncClient`, Pydantic settings, pytest, RESPX, Docker Compose or Testcontainers-style integration tests.

_Build and Deployment Systems:_ `pyproject.toml`, pinned dependencies, Dockerfile, Docker Compose test fixture, and later CI matrix for selected GeoServer versions.

_Source:_ [HTTPX async support](https://www.python-httpx.org/async/), [HTTPX timeouts](https://www.python-httpx.org/advanced/timeouts/), [Pydantic settings](https://pydantic.dev/docs/validation/dev/api/pydantic_settings/), [Testcontainers Python guide](https://docs.docker.com/guides/testcontainers-python-getting-started/)

## 4. Technology Stack Evolution and Current Trends

### Current Technology Stack Landscape

_Programming Languages:_ Python and TypeScript are both official MCP SDK ecosystems. Python is preferred here because the domain is GeoServer/OGC diagnostics, XML parsing, filesystem evidence, and operational tooling.

_Frameworks and Libraries:_ Official Python MCP SDK / FastMCP should be the MCP layer. Avoid wrapper frameworks until the core contract is stable.

_Database and Storage Technologies:_ No product-owned database in v1. Use config file/env/secrets and request-scoped cache only.

_API and Communication Technologies:_ Streamable HTTP for Dockerized MCP transport, optional stdio for local development, HTTP/HTTPS for GeoServer REST/OGC.

_Source:_ [MCP SDKs](https://modelcontextprotocol.io/docs/sdk), [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk), [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)

### Technology Adoption Patterns

Adopt MCP and GeoServer coverage incrementally:

- First prove MCP server lifecycle and one GeoServer check.
- Then add normalized catalog inventory.
- Then add OGC capabilities.
- Then diagnostics and comparison.
- Then optional Data Directory enrichment.

_Adoption Trends:_ MCP is moving toward stable server contracts and production concerns such as transports, error semantics, observability, and tool safety.

_Migration Patterns:_ Keep MCP SDK usage isolated behind an adapter so SDK changes do not rewrite domain logic.

_Emerging Technologies:_ Streamable HTTP matters for independent Dockerized MCP servers, but client compatibility should be confirmed during architecture.

_Source:_ [MCP transports](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports), [Bridging Protocol and Production](https://arxiv.org/abs/2603.13417)

## 5. Integration and Interoperability Patterns

### Current Integration Approaches

GeoServer MCP should be an anti-corruption layer between AI agents and GeoServer. AI agents should interact with stable concepts, not raw REST endpoints or raw OGC XML.

_API Design Patterns:_ Task-level tools, not endpoint-level tools.

_Service Integration:_ Direct HTTP/HTTPS calls to configured GeoServer instances.

_Data Integration:_ REST JSON/XML, OGC capabilities XML, and optional Data Directory XML/config evidence normalized into internal models.

_Source:_ [GeoServer REST docs](https://docs.geoserver.org/stable/en/user/rest/index.html), [GeoServer WMS reference](https://docs.geoserver.org/latest/en/user/services/wms/reference/), [GeoServer WFS reference](https://geoserver.org/geoserver/en/user/services/wfs/reference/)

### Interoperability Standards and Protocols

_Standards Compliance:_ MCP for agent integration; GeoServer REST for catalog/config inventory; OGC WMS/WFS/WCS/WMTS capabilities for advertised service visibility.

_Protocol Selection:_ Streamable HTTP or stdio for MCP; HTTP/HTTPS for GeoServer; XML and JSON parsing internally.

_Integration Challenges:_ GeoServer version differences, endpoint availability, virtual services, large capabilities documents, auth differences, partial failures, optional filesystem access.

_Source:_ [MCP server concepts](https://modelcontextprotocol.io/docs/learn/server-concepts), [GeoServer virtual services](https://docs.geoserver.org/main/en/user/configuration/virtual-services/), [GeoServer services docs](https://docs.geoserver.org/main/en/user/services/index.html)

## 6. Performance and Scalability Analysis

### Performance Characteristics and Optimization

The performance bottlenecks are outbound GeoServer calls, slow instances, large OGC capabilities documents, and repeated inventory requests. Python is sufficient because the workload is mostly I/O and parsing.

_Optimization Strategies:_ Bounded async concurrency, explicit timeouts, request-scoped cache, summary/detail separation, and avoiding raw response dumps.

_Monitoring and Measurement:_ Log per-instance request failures, timeout counts, parse failures, redaction events, and diagnostic generation status.

_Source:_ [HTTPX timeouts](https://www.python-httpx.org/advanced/timeouts/), [MCP transports](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)

### Scalability Patterns and Approaches

_Scalability Patterns:_ Single-process concurrency with bounded fan-out; no distributed services in v1.

_Capacity Planning:_ Architecture should define default total timeout, per-request timeout, max concurrent instances, max concurrent requests per instance, and maximum response/report size.

_Elasticity and Auto-scaling:_ Not a v1 concern. Self-hosted Dockerized operation is the target.

_Source:_ [HTTPX async support](https://www.python-httpx.org/async/), [Bridging Protocol and Production](https://arxiv.org/abs/2603.13417)

## 7. Security and Compliance Considerations

### Security Best Practices and Frameworks

GeoServer MCP holds administrator-equivalent credentials and exposes operational tools to AI agents, so the security baseline must be strict.

_Security Frameworks:_ OWASP SSRF guidance, OWASP XXE guidance, and OWASP secrets-management guidance are directly relevant.

_Threat Landscape:_ Prompt/tool misuse, SSRF via crafted targets, XML parser attacks, credential leakage, overbroad filesystem access, and accidental mutation.

_Secure Development Practices:_ No generic HTTP tool, configured target allowlist, redirect control, GET-only client methods, safe XML parsing, redaction tests, and read-only Data Directory mounts.

_Source:_ [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html), [OWASP XXE Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html), [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

### Compliance and Regulatory Considerations

No formal regulatory compliance target is defined for v1. However, the product should be governance-friendly:

- Redact secrets and sensitive store metadata.
- Preserve evidence source metadata for findings.
- Clearly report unknown and unavailable information.
- Avoid write/admin operations in v1.

_Industry Standards:_ OGC service protocols and MCP protocol/spec behavior.

_Audit and Governance:_ Diagnostic reports should be copyable into operational handoff or issue tracking.

_Source:_ [GeoServer REST docs](https://docs.geoserver.org/stable/en/user/rest/index.html), [MCP server concepts](https://modelcontextprotocol.io/docs/learn/server-concepts)

## 8. Strategic Technical Recommendations

### Technical Strategy and Decision Framework

_Architecture Recommendations:_ Python modular monolith, hexagonal boundaries, REST/OGC primary evidence, optional Data Directory evidence, task-level MCP tools.

_Technology Selection:_ Python, official Python MCP SDK / FastMCP, `httpx`, Pydantic settings, pytest, RESPX, Docker Compose/Testcontainers-style fixtures.

_Implementation Strategy:_ Build vertical slices, prove read-only safety, define contracts before broad endpoint coverage, and make diagnostic reason codes stable early.

_Source:_ [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk), [HTTPX async support](https://www.python-httpx.org/async/), [Pydantic settings](https://pydantic.dev/docs/validation/dev/api/pydantic_settings/)

### Competitive Technical Advantage

GeoServer MCP's advantage is not endpoint breadth alone. Its advantage is GeoServer-aware normalization, diagnostics, partial-access honesty, and safe AI-agent operation across multiple instances.

_Technology Differentiation:_ A domain-specific operations assistant rather than a generic REST bridge.

_Innovation Opportunities:_ Drift detection, usage statistics integration, safe catalog CRUD, governance snapshots, and extension-aware diagnostics.

_Strategic Technology Investments:_ Diagnostic taxonomy, normalized evidence model, secure MCP surface, and real GeoServer integration fixtures.

_Source:_ [GeoServer monitoring extension](https://docs.geoserver.org/main/en/user/extensions/monitoring/), [GeoServer REST docs](https://docs.geoserver.org/stable/en/user/rest/index.html)

## 9. Implementation Roadmap and Risk Assessment

### Technical Implementation Framework

_Implementation Phases:_

1. Scaffold Python package, Dockerfile, config model, logging, tests, and MCP startup.
2. Implement config/env/secrets loading and validation.
3. Implement safe GeoServer HTTP client with basic auth and structured errors.
4. Implement `check_instances`.
5. Implement REST inventory for workspaces, stores, layers/layer groups, and styles.
6. Implement WMS/WFS capabilities first, then WCS/WMTS.
7. Implement diagnostic finding model and reason-code taxonomy.
8. Implement compare/report tools and partial-access reporting.
9. Add optional Data Directory status and one minimal Data Directory-derived diagnostic.
10. Build Docker Compose integration fixture with GeoServer and optional PostGIS.

_Technology Migration Strategy:_ No migration needed for greenfield. Keep future SDK or transport changes isolated in the MCP adapter.

_Resource Planning:_ Solo-developer friendly if broken into BMAD stories by vertical slice.

_Source:_ [GeoServer Docker install docs](https://docs.geoserver.org/stable/en/user/installation/docker.html), [pytest docs](https://pytest.org/en/stable/)

### Technical Risk Management

_Technical Risks:_

- MCP SDK churn.
- GeoServer version differences.
- Over-broad MCP surface.
- Credential leakage.
- SSRF and unsafe XML parsing.
- False-positive diagnostics.
- Data Directory assumptions.
- Slow or large deployments.

_Mitigations:_

- Pin SDK versions and isolate adapters.
- Capability-detect and test selected GeoServer versions.
- Avoid generic HTTP/file tools.
- Centralize redaction and test it.
- Enforce allowlisted targets and safe XML parser settings.
- Attach evidence to findings.
- Treat Data Directory as optional.
- Use bounded concurrency and timeouts.

_Source:_ [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html), [OWASP XXE Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html), [Bridging Protocol and Production](https://arxiv.org/abs/2603.13417)

## 10. Future Technical Outlook and Innovation Opportunities

### Emerging Technology Trends

_Near-term Technical Evolution:_ MCP transports, SDKs, and production patterns will continue to evolve. Keep the adapter thin.

_Medium-term Technology Trends:_ GeoServer 3.x introduces a major-version compatibility question; architecture should decide whether v1 targets GeoServer 2.28 stable, GeoServer 3.x, or both.

_Long-term Technical Vision:_ GeoServer MCP can evolve from read-only diagnostics into safe governance and admin automation, including catalog CRUD, usage statistics, and drift detection.

_Source:_ [GeoServer 3.0-RC release](https://geoserver.org/announcements/2026/04/20/geoserver-3-0-RC-released.html), [MCP transports](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)

### Innovation and Research Opportunities

_Research Opportunities:_ Version compatibility matrix, diagnostic rule quality, OGC parser coverage, monitoring-extension integration, and safe write/admin workflows.

_Emerging Technology Adoption:_ Add Streamable HTTP-first deployment only after confirming target MCP client compatibility.

_Innovation Framework:_ Add capabilities only after they strengthen the evidence/diagnostic model rather than widening endpoint exposure.

_Source:_ [GeoServer monitoring extension](https://docs.geoserver.org/main/en/user/extensions/monitoring/), [MCP server concepts](https://modelcontextprotocol.io/docs/learn/server-concepts)

## 11. Technical Research Methodology and Source Verification

### Comprehensive Technical Source Documentation

_Primary Technical Sources:_

- MCP server concepts and transports.
- Official MCP Python and TypeScript SDK repositories.
- GeoServer REST, OGC service, Data Directory, Docker, and monitoring docs.
- OWASP SSRF, XXE, and secrets-management cheat sheets.

_Secondary Technical Sources:_

- MCP production pattern research.
- Docker/Testcontainers/pytest/HTTPX/Pydantic/RESPX documentation.

_Technical Web Search Queries Used:_

- Official MCP Python/TypeScript SDKs.
- MCP tools/resources/prompts and transports.
- GeoServer REST catalog resources and status endpoints.
- GeoServer OGC WMS/WFS/WCS/WMTS capabilities.
- GeoServer Docker images and installation.
- OWASP SSRF, XXE, and secrets management.
- Python HTTP/config/testing libraries.

### Technical Research Quality Assurance

_Technical Source Verification:_ Product-critical facts were checked against official MCP, GeoServer, Docker/tooling, and OWASP sources where possible.

_Technical Confidence Levels:_

- High: Python-first architecture, REST/OGC primary evidence, Dockerized server, read-only v1, task-level MCP tools.
- Medium: exact OGC parser library and exact MCP transport mix, because this depends on architecture and target client compatibility.
- Open: supported GeoServer version matrix and depth of Data Directory diagnostics.

_Technical Limitations:_ This research did not run live GeoServer fixtures. Architecture should validate endpoint behavior against real containers before epics/stories are finalized.

## 12. Technical Appendices and Reference Materials

### Initial Diagnostic Reason Codes

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

### Suggested Initial MCP Tool Groups

- Instance connection and status.
- Catalog inventory.
- Service capability inventory.
- Catalog resource detail lookup.
- Instance comparison.
- Diagnostic finding/report generation.
- Optional Data Directory status and evidence reporting.

### Technical Resources and References

- [MCP server concepts](https://modelcontextprotocol.io/docs/learn/server-concepts)
- [MCP transports specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [GeoServer REST docs](https://docs.geoserver.org/stable/en/user/rest/index.html)
- [GeoServer Docker install docs](https://docs.geoserver.org/stable/en/user/installation/docker.html)
- [GeoServer data directory structure](https://geoserver.org/geoserver/en/user/datadirectory/structure/)
- [GeoServer monitoring extension](https://docs.geoserver.org/main/en/user/extensions/monitoring/)
- [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP XXE Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html)

---

## Technical Research Conclusion

### Summary of Key Technical Findings

GeoServer MCP should be a Dockerized Python MCP server that exposes normalized, read-only GeoServer inventory and diagnostics to AI agents. The correct abstraction is not a raw REST wrapper; it is a GeoServer-aware evidence and diagnostics layer with stable MCP operations.

### Strategic Technical Impact Assessment

This architecture creates a disciplined foundation for future management operations. By proving inventory, diagnostics, redaction, partial-access handling, and testing against real GeoServer containers first, the project can later add CRUD/admin tools without retrofitting safety into an unsafe surface.

### Next Steps Technical Recommendations

Proceed to `$bmad-create-architecture` using this research plus the PRD. The architecture step should finalize the Python package structure, MCP tool/resource contract, response schemas, diagnostic taxonomy, supported GeoServer version matrix, exact XML parser choice, timeout/concurrency defaults, and Docker Compose test fixture.

---

**Technical Research Completion Date:** 2026-05-27  
**Research Period:** current comprehensive technical analysis  
**Source Verification:** All major technical claims cited with current sources  
**Technical Confidence Level:** High for architecture direction; medium for exact library/runtime details pending architecture validation

_This comprehensive technical research document is intended as the technical input to BMAD architecture creation for GeoServer MCP._
