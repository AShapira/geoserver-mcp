# Story 1.3: Implement Safe GeoServer HTTP Client for Read-Only Access

Status: done

## Story

As a GeoServer administrator,
I want the MCP server to make safe authenticated read-only GeoServer requests,
so that connectivity checks cannot accidentally mutate GeoServer state.

## Acceptance Criteria

1. Given a configured GeoServer instance with basic auth credentials, when the HTTP client performs a connectivity request, then it uses HTTP/HTTPS GET-only access, applies configured timeouts, and does not follow unsafe redirects by default.
2. Given an outbound request target is not derived from a configured GeoServer base URL, when the HTTP client is asked to call it, then the request is rejected before network access and the result uses an appropriate reason code.
3. Given the GeoServer response is 401, 403, 404, timeout, or malformed, when the client maps the result, then it returns a structured error using the shared `ReasonCode` taxonomy and raw adapter exceptions do not leak into MCP responses.

## Tasks / Subtasks

- [x] Add shared domain result primitives. (AC: 2, 3)
  - [x] Add `ReasonCode` under `src/geoserver_mcp/domain/` with the architecture-defined values needed now: `network_error`, `auth_failed`, `forbidden`, `not_found`, `unsupported_endpoint`, `parse_error`, and `unknown`.
  - [x] Add a small structured adapter result/error model for GeoServer HTTP calls that carries status, reason code, redacted message, optional HTTP status, and redacted evidence URL.
  - [x] Export only stable domain primitives from `src/geoserver_mcp/domain/__init__.py`.
- [x] Add direct HTTP client dependencies. (AC: 1, 3)
  - [x] Add `httpx>=0.28,<1.0` as a direct runtime dependency.
  - [x] Add `respx>=0.22,<1.0` or the current compatible HTTPX mocking package as a dev dependency.
  - [x] Regenerate `uv.lock`.
- [x] Implement the safe GeoServer REST client under `src/geoserver_mcp/adapters/geoserver_rest/`. (AC: 1, 2, 3)
  - [x] Create a client that accepts a `RuntimeInstanceConfig`, builds requests only from that instance's configured `base_url`, and only performs `GET`.
  - [x] Provide a connectivity-oriented method that requests a safe relative endpoint, defaulting to GeoServer REST about/version metadata such as `rest/about/version.json`.
  - [x] Configure bounded timeouts and disable automatic redirects by default.
  - [x] Reject absolute URLs, scheme-relative URLs, path traversal attempts, and paths that resolve outside the configured base URL before network access.
  - [x] Apply basic auth credentials from Story 1.2 runtime config without exposing secret values through `repr`, errors, logs, or returned objects.
  - [x] Map HTTP 401 to `auth_failed`, 403 to `forbidden`, 404 to `not_found`, timeout/network failures to `network_error`, malformed JSON/body mapping failures to `parse_error`, unsupported or unsafe targets to `unsupported_endpoint`, and unexpected failures to `unknown`.
- [x] Add focused tests for safe HTTP behavior. (AC: 1, 2, 3)
  - [x] Add unit tests proving the client issues GET requests only, sends basic auth, applies a configured timeout, and does not follow redirects automatically.
  - [x] Add tests proving unsafe targets are rejected before any mocked network request is observed.
  - [x] Add tests for 401, 403, 404, timeout/network, malformed response, and unexpected exception mappings.
  - [x] Add redaction assertions proving usernames, passwords, and credential-bearing URLs do not appear in returned errors, reprs, or log-like strings.
- [x] Preserve Story 1.1 and 1.2 behavior. (AC: all)
  - [x] Do not register `check_instances` or any new MCP tool in this story; Story 1.4 owns tool exposure.
  - [x] Keep MCP SDK imports isolated under `src/geoserver_mcp/adapters/mcp/`.
  - [x] Keep config loading network-free.
  - [x] Confirm `geoserver-mcp --version` and MCP app construction still work without a config file.
- [x] Run and document the quality gate. (AC: all)
  - [x] Run `.\.venv\Scripts\uv.exe run ruff format --check .`.
  - [x] Run `.\.venv\Scripts\uv.exe run ruff check .`.
  - [x] Run `.\.venv\Scripts\uv.exe run pytest`.
  - [x] Run `git diff --check`.
  - [x] Run Docker build because dependencies and packaged files changed.
  - [x] Update this story's Dev Agent Record, File List, and Change Log only after checks pass.

### Review Findings

- [x] [Review][Patch] Percent-encoded traversal or separators can bypass the relative path safety check [src/geoserver_mcp/adapters/geoserver_rest/client.py:141]
- [x] [Review][Patch] Redirect handling and successful response redaction need explicit regression tests [tests/unit/test_geoserver_rest_client.py:36]

## Dev Notes

### Source Context

- Story source: `_bmad-output/planning-artifacts/epics.md` Story 1.3.
- Architecture source: `_bmad-output/planning-artifacts/architecture.md` Data Architecture, Authentication & Security, API & Communication Patterns, Error Handling Patterns, Project Structure & Boundaries.
- PRD source: `_bmad-output/planning-artifacts/prds/prd-geoserver-mcp-2026-05-25/prd.md` FR-17, FR-18, FR-19 and NFR-1, NFR-2, NFR-7.
- Previous story source: `_bmad-output/implementation-artifacts/1-2-load-multi-instance-configuration-and-secret-references.md`.

### Architecture Requirements

- Put GeoServer HTTP access only under `src/geoserver_mcp/adapters/geoserver_rest/`.
- Do not create a generic URL fetcher or raw endpoint proxy. The adapter may accept safe relative paths only.
- Outbound requests must be derived from configured `RuntimeInstanceConfig.base_url`.
- v1 is read-only: no POST, PUT, PATCH, DELETE, reload, purge, or mutation helpers.
- Redirects are disabled by default. Do not silently follow redirects to a different origin.
- All external failures map to `ReasonCode`; raw `httpx` or adapter exceptions must not leave the adapter.
- All user-visible output must be redacted with the existing `security.redaction` utilities.
- Do not implement MCP tool registration, `check_instances`, catalog inventory, OGC parsing, Data Directory reads, or Docker GeoServer fixtures in this story.

### Current Code To Preserve

- `src/geoserver_mcp/config/secrets.py` already resolves `RuntimeInstanceConfig` with `base_url`, optional `data_directory`, and redaction-safe `BasicCredentials`.
- `src/geoserver_mcp/config/loader.py` is intentionally network-free and must stay that way.
- `src/geoserver_mcp/adapters/mcp/server.py` can construct a FastMCP app without configuration; this must still pass.
- `src/geoserver_mcp/security/redaction.py` already redacts known secret values and credential-bearing keys; reuse it instead of creating another redaction path.

### Implementation Guidance

- Use `httpx.AsyncClient` and keep the adapter async-ready for later MCP tools.
- Prefer a small adapter result model over raising for expected external failures.
- Use `RuntimeInstanceConfig.credentials.as_basic_auth_tuple()` only at request construction time.
- For URL safety, combine the configured base URL with a relative endpoint using structured URL parsing, then verify scheme and origin still match the configured instance.
- Treat invalid relative paths and cross-origin/absolute targets as `unsupported_endpoint` without issuing a request.
- A malformed connectivity response means the HTTP request succeeded but the body could not be interpreted as expected; map it to `parse_error`.

### Testing Requirements

- Tests must be local and deterministic. Use mocked HTTP; do not require a live GeoServer instance.
- Tests must prove unsafe target rejection happens before network access.
- Tests must prove returned failures contain reason codes and redacted messages, not raw exception objects or secrets.
- Add at least one regression test proving config loading still performs no network calls.
- Keep Docker fixture work out of this story; Story 1.6 owns real-container integration.

### Anti-Patterns To Avoid

- Do not return raw GeoServer responses as public data.
- Do not add MCP tools or prompts.
- Do not expose configured username/password in errors, reprs, logs, test assertion messages, or README examples.
- Do not allow absolute request URLs, scheme-relative paths, `..` traversal, or redirect-following by default.
- Do not add retries, caching, background health checks, or persistent connection state beyond the request/client lifecycle needed here.

## Project Structure Notes

The current checkout has package skeletons but no GeoServer REST implementation yet. Story 1.3 should fill the adapter and shared domain primitives narrowly enough for Story 1.4 to orchestrate `check_instances` without revisiting safety fundamentals.

## References

- [Source: epics.md Story 1.3](../planning-artifacts/epics.md)
- [Source: architecture.md Authentication & Security, Error Handling, Structure Patterns](../planning-artifacts/architecture.md)
- [Source: prd.md FR-17, FR-18, FR-19, NFR-1, NFR-2, NFR-7](../planning-artifacts/prds/prd-geoserver-mcp-2026-05-25/prd.md)
- [Previous story: Story 1.2 config and secret handling](1-2-load-multi-instance-configuration-and-secret-references.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- 2026-06-21: Created Story 1.3 and marked it ready for development.
- 2026-06-21: Started Story 1.3 implementation.
- 2026-06-21: Added `httpx>=0.28,<1.0` runtime dependency and `respx>=0.22,<1.0` dev dependency with `.\.venv\Scripts\uv.exe`.
- 2026-06-21: Confirmed red phase with `.\.venv\Scripts\uv.exe run pytest tests\unit\test_geoserver_rest_client.py` failing on missing `GeoServerRestClient`.
- 2026-06-21: `.\.venv\Scripts\uv.exe run pytest tests\unit\test_geoserver_rest_client.py` passed with 11 tests.
- 2026-06-21: `.\.venv\Scripts\uv.exe run ruff format --check .` passed.
- 2026-06-21: `.\.venv\Scripts\uv.exe run ruff check .` passed with a non-fatal `.ruff_cache` write warning.
- 2026-06-21: `.\.venv\Scripts\uv.exe run pytest` passed with 39 tests and the existing pytest cache access warning.
- 2026-06-21: `.\.venv\Scripts\uv.exe run geoserver-mcp --version` returned `geoserver-mcp 0.1.0`.
- 2026-06-21: MCP app construction smoke check returned `FastMCP`.
- 2026-06-21: `git diff --check` passed with LF-to-CRLF warnings only.
- 2026-06-21: `docker build -t geoserver-mcp:story-1-3 .` passed.
- 2026-06-21: BMAD code review completed with 0 decision-needed, 2 patch, 0 deferred findings.
- 2026-06-21: Applied review patches for percent-encoded URL traversal/separator rejection and redirect/redaction regression tests.
- 2026-06-21: `.\.venv\Scripts\uv.exe run pytest tests\unit\test_geoserver_rest_client.py` passed with 16 tests.
- 2026-06-21: `.\.venv\Scripts\uv.exe run ruff format --check .` passed.
- 2026-06-21: `.\.venv\Scripts\uv.exe run ruff check .` passed.
- 2026-06-21: `.\.venv\Scripts\uv.exe run pytest` passed with 44 tests and the existing pytest cache access warning.
- 2026-06-21: `git diff --check` passed with LF-to-CRLF warnings only.
- 2026-06-21: `docker build -t geoserver-mcp:story-1-3-review .` passed.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added the shared `ReasonCode` taxonomy under `domain`.
- Added a redaction-safe GeoServer REST result model and async GET-only client under `adapters/geoserver_rest`.
- Added direct runtime/dev dependencies for HTTP access and HTTPX request mocking.
- Added mocked HTTP tests covering GET-only behavior, basic auth, timeout/redirect settings, unsafe target pre-network rejection, reason-code mapping, malformed responses, and redaction.
- Preserved config loading and MCP app construction behavior; no MCP tools were registered in this story.
- Resolved all Story 1.3 code review findings and moved the story to done.

### File List

- _bmad-output/implementation-artifacts/1-3-implement-safe-geoserver-http-client-for-read-only-access.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- pyproject.toml
- uv.lock
- src/geoserver_mcp/adapters/geoserver_rest/__init__.py
- src/geoserver_mcp/adapters/geoserver_rest/client.py
- src/geoserver_mcp/domain/__init__.py
- src/geoserver_mcp/domain/enums.py
- tests/unit/test_geoserver_rest_client.py

### Change Log

- 2026-06-21: Created Story 1.3 and marked it ready for development.
- 2026-06-21: Moved Story 1.3 to in-progress.
- 2026-06-21: Implemented safe GET-only GeoServer REST client, reason-code mapping, tests, and quality gates; moved story to review.
- 2026-06-21: Applied code review patches, reran quality gates, and marked Story 1.3 done.
