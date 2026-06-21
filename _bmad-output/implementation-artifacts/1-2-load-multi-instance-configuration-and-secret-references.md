# Story 1.2: Load Multi-Instance Configuration and Secret References

Status: done

## Story

As a GeoServer administrator,
I want to configure multiple GeoServer instances using a config file and environment-provided secrets,
so that the MCP server can inspect real deployments without hardcoding credentials.

## Acceptance Criteria

1. Given a valid config file with multiple instance definitions, when the server loads configuration, then each instance has a unique ID, base URL, auth reference, and optional Data Directory path, and duplicate instance IDs fail validation with an actionable error.
2. Given credentials are referenced through environment variables, when config is loaded, then the resolved runtime config can authenticate requests, and secret values are not exposed in normal config display, logs, or validation errors.
3. Given required fields are missing or invalid, when config validation runs, then startup fails with structured validation errors, and no GeoServer network calls are attempted.

## Tasks / Subtasks

- [x] Add direct configuration dependencies and preserve existing scaffold behavior. (AC: 1, 2, 3)
  - [x] Add direct runtime dependencies for Pydantic v2, `pydantic-settings`, and YAML parsing to `pyproject.toml`; regenerate `uv.lock`.
  - [x] Keep Python constrained to `>=3.13,<3.14` and do not add HTTP clients, GeoServer fixtures, or `check_instances` in this story.
  - [x] Confirm `geoserver-mcp --version` and the existing app-construction smoke test still work without a config file.
- [x] Implement typed configuration models under `src/geoserver_mcp/config/`. (AC: 1, 3)
  - [x] Add a config model for the whole app and a per-instance model with fields: `id`, `base_url`, `auth`, and optional `data_directory`.
  - [x] Model `auth` as a secret reference, not an inline password value. At minimum support basic auth references with `username_env` and `password_env`.
  - [x] Validate duplicate instance IDs with a clear, deterministic validation error.
  - [x] Validate `base_url` as HTTP/HTTPS only and reject missing, relative, or non-HTTP URLs before any network code can run.
  - [x] Validate optional `data_directory` as a path reference only; do not inspect the filesystem yet.
- [x] Implement config file loading with structured errors and no network side effects. (AC: 1, 3)
  - [x] Add a loader module that reads a YAML config file from an explicit path and returns the typed app config.
  - [x] Use safe YAML loading only; never use object-constructing YAML load APIs.
  - [x] Convert file-not-found, parse, schema, and validation failures into project-owned config error types or structured error objects.
  - [x] Ensure config loading does not import or call GeoServer REST, OGC, Data Directory inspection, MCP tools, or any outbound network client.
- [x] Implement environment secret resolution with redaction-safe runtime objects. (AC: 2)
  - [x] Add a resolver that reads secret values from environment variables named by the config file.
  - [x] Return a runtime credential object usable by later HTTP client work without exposing the secret through `repr`, `str`, `model_dump`, logs, or validation messages.
  - [x] Produce actionable errors for missing referenced env vars while redacting secret variable values.
  - [x] Do not persist resolved secret values in the config file model, examples, story notes, or tests.
- [x] Add redaction helpers in `src/geoserver_mcp/security/`. (AC: 2)
  - [x] Add a small redaction utility for known secret values, credential-bearing keys, and auth structures.
  - [x] Use the utility in config error rendering and any public config display helper added in this story.
  - [x] Add tests proving secret values are absent from normal dumps, reprs, errors, and log-like formatted output.
- [x] Add config examples and runtime documentation. (AC: 1, 2, 3)
  - [x] Add `examples/geoserver-mcp.yaml` with two sample instances that reference env vars but contain no real or default GeoServer passwords.
  - [x] Add `examples/geoserver-mcp.env.example` with placeholder env var names and non-secret placeholder values only.
  - [x] Update `README.md` with the config path/env secret pattern and the expected validation behavior.
  - [x] If CLI wiring for config path is added, use a neutral env var such as `GEOSERVER_MCP_CONFIG` and keep startup error messages structured and redacted.
- [x] Add focused unit tests. (AC: 1, 2, 3)
  - [x] Add `tests/unit/test_config_loader.py` for valid multi-instance YAML, duplicate IDs, missing required fields, invalid URL schemes, and YAML parse errors.
  - [x] Add `tests/unit/test_secret_resolution.py` for env-secret resolution, missing env vars, and redaction of secret values.
  - [x] Add `tests/unit/test_redaction.py` for credential-key and known-secret redaction behavior.
  - [x] Keep tests local and deterministic; they must not require a live GeoServer instance, Docker fixture, local Data Directory, or network access.
- [x] Run and document the quality gate. (AC: all)
  - [x] Run `.\.venv\Scripts\uv.exe run pytest`.
  - [x] Run `.\.venv\Scripts\uv.exe run ruff check --no-cache .`.
  - [x] Run `.\.venv\Scripts\uv.exe run ruff format --check --no-cache .`.
  - [x] Run `docker --config .\.docker-config build --tag geoserver-mcp:dev .` if dependencies or packaged files changed.
  - [x] Update this story's Dev Agent Record, File List, and Change Log only after the checks pass.

### Review Findings

- [x] [Review][Patch] Credential-bearing `base_url` values bypass env-secret references and can leak through normal display [src/geoserver_mcp/config/models.py:29]
- [x] [Review][Patch] Data Directory path references use host `Path` semantics and the valid-config test is Windows-only [tests/unit/test_config_loader.py:40]
- [x] [Review][Patch] Empty secret environment values resolve as valid credentials [src/geoserver_mcp/config/secrets.py:82]
- [x] [Review][Patch] Overlapping known secrets can be partially leaked during text redaction [src/geoserver_mcp/security/redaction.py:17]
- [x] [Review][Patch] Duplicate YAML keys are silently accepted before validation [src/geoserver_mcp/config/loader.py:24]
- [x] [Review][Patch] `AppConfig` remains mutable through its `instances` list after validation [src/geoserver_mcp/config/models.py:44]
- [x] [Review][Patch] Invalid UTF-8 config files can bypass project-owned parse errors [src/geoserver_mcp/config/loader.py:22]
- [x] [Review][Patch] Environment variable reference names allow invalid or log-shaping characters [src/geoserver_mcp/config/models.py:16]
- [x] [Review][Patch] Structured redaction misses common credential key names such as `api_key` and `access_key` [src/geoserver_mcp/security/redaction.py:7]
- [x] [Review][Patch] Tests do not guard config loading against accidental network side effects [tests/unit/test_config_loader.py:13]

## Dev Notes

### Source Context

- Story source: `_bmad-output/planning-artifacts/epics.md` Story 1.2, lines 247-267.
- PRD source: `_bmad-output/planning-artifacts/prds/prd-geoserver-mcp-2026-05-25/prd.md` FR-1, FR-2, FR-19, NFR-1, NFR-2, NFR-7, MVP scope, and success metrics.
- Architecture source: `_bmad-output/planning-artifacts/architecture.md` stack decisions, module boundaries, source organization, deployment structure, and testing structure.
- Previous story source: `_bmad-output/implementation-artifacts/1-1-initialize-dockerized-python-mcp-server-scaffold.md`.

### Architecture Requirements

- Implement configuration code under `src/geoserver_mcp/config/`; do not put business logic in `server.py`.
- Put secret redaction helpers under `src/geoserver_mcp/security/`.
- Keep MCP SDK imports isolated under `src/geoserver_mcp/adapters/mcp/`; Story 1.1 code review fixed this boundary and Story 1.2 must not regress it.
- Do not add GeoServer REST calls, OGC parsing, Data Directory inspection, MCP tools, `check_instances`, a database, queue, dashboard, or generic HTTP proxy.
- Config loading is allowed to validate URL shape and secret references, but it must not check reachability or authentication. That starts in Story 1.3 and Story 1.4.
- Preserve current CLI behavior: the server can still report `--version` and construct the MCP app without requiring GeoServer configuration.

### Proposed Config Shape

Use a simple YAML shape unless implementation finds a stronger reason to change it:

```yaml
instances:
  - id: production
    base_url: https://geoserver.example.com/geoserver
    auth:
      type: basic
      username_env: GEOSERVER_PROD_USER
      password_env: GEOSERVER_PROD_PASSWORD
    data_directory: /mnt/geoserver-prod-data
  - id: staging
    base_url: https://staging-geoserver.example.com/geoserver
    auth:
      type: basic
      username_env: GEOSERVER_STAGING_USER
      password_env: GEOSERVER_STAGING_PASSWORD
```

Implementation details:

- `id` should be stable, non-empty, and suitable for use in tool responses. Prefer a conservative pattern such as letters, digits, `_`, and `-`.
- `base_url` should normalize enough to be useful later but must not silently rewrite unsafe or unsupported schemes.
- `auth.type` should be explicit so later auth types can be added without reshaping the config.
- `data_directory` remains a configured path only in this story; path containment and actual filesystem checks belong to Epic 5.

### Dependency Guidance

- Add direct dependencies rather than relying on transitive dependencies from `mcp`.
- Pydantic Settings documentation says `BaseSettings` reads missing field values from environment variables and supports environment/secrets loading. Use this for env integration where it fits, but keep config-file parsing explicit and testable.
- Current PyPI check on 2026-06-21 found `pydantic-settings` 2.14.2 released 2026-06-19. A reasonable dependency constraint is `pydantic-settings>=2.14,<3.0`.
- Use Pydantic v2 models and validators for config shape and duplicate-ID checks.
- Use PyYAML only through `safe_load`; PyYAML documentation warns that ordinary `load` can construct arbitrary Python objects, while `safe_load` limits construction to simple Python objects. Current PyPI check found PyYAML 6.0.3 as current.
- Do not add `httpx`, `respx`, XML parsers, or Docker GeoServer fixtures in this story.

### Previous Story Intelligence

- Story 1.1 created the package scaffold, Docker runtime, CI, and the architecture directory skeleton.
- Story 1.1 review found and fixed: unresolved `astral-sh/setup-uv@v8`, MCP SDK imports outside `adapters/mcp`, raw env validation tracebacks, build-only Docker CI, and all-interface Compose publishing.
- Keep the improved CLI validation style from `src/geoserver_mcp/__main__.py`: bad operator input should become controlled argparse/config errors, not raw tracebacks.
- Current local command pattern uses `.\.venv\Scripts\uv.exe` because `uv` may not be on PATH in this workspace.

### File Structure Requirements

Expected new or updated files:

```text
pyproject.toml
uv.lock
README.md
examples/geoserver-mcp.yaml
examples/geoserver-mcp.env.example
src/geoserver_mcp/config/__init__.py
src/geoserver_mcp/config/errors.py
src/geoserver_mcp/config/loader.py
src/geoserver_mcp/config/models.py
src/geoserver_mcp/config/secrets.py
src/geoserver_mcp/security/__init__.py
src/geoserver_mcp/security/redaction.py
tests/unit/test_config_loader.py
tests/unit/test_secret_resolution.py
tests/unit/test_redaction.py
```

Only add more files if needed to keep responsibilities clean. If names differ, keep the same ownership boundaries.

### Testing Requirements

- Valid config test: two instances load with unique IDs, base URLs, auth refs, and optional data-directory path.
- Duplicate ID test: duplicate instance IDs fail with a deterministic message that names the duplicated ID but does not include secret values.
- Secret resolution test: env refs resolve into a runtime credential object usable by later code.
- Missing secret test: missing env var names are reported; secret values are never printed.
- Redaction tests: config dumps, reprs, exceptions, and log-like messages must not contain the resolved username/password values.
- Invalid config tests: missing required fields, invalid URL scheme, YAML parse error, and non-list `instances`.
- No-network guard: tests should prove or make clear that config loading does not call any GeoServer/network adapter.

### Anti-Patterns To Avoid

- Do not put raw passwords in YAML examples, tests, `README.md`, exceptions, or logs.
- Do not support inline password values in the main config unless a later product decision explicitly allows it.
- Do not create a generic "URL fetcher" or endpoint proxy.
- Do not validate credentials by making a network request.
- Do not implement `check_instances`; that belongs to Story 1.4.
- Do not move MCP app creation back into non-adapter modules.
- Do not inspect or validate the Data Directory path on disk in this story.
- Do not rely on transitive dependencies for direct application code imports.

## Project Structure Notes

The current checkout already contains the Story 1.1 scaffold under `src/geoserver_mcp/`. Story 1.2 should extend the existing empty `config/` and `security/` packages instead of creating parallel modules elsewhere. The architecture document contains an older ideal path `adapters/mcp/app.py`, but the actual scaffold now uses `adapters/mcp/server.py`; preserve the current working shape unless the implementation has a clear reason to rename it.

## References

- [Source: epics.md Story 1.2](../planning-artifacts/epics.md)
- [Source: prd.md FR-1, FR-2, FR-19, NFR-1, NFR-7](../planning-artifacts/prds/prd-geoserver-mcp-2026-05-25/prd.md)
- [Source: architecture.md Config, Validation, Project Structure, Deployment Structure](../planning-artifacts/architecture.md)
- [Previous story: Story 1.1 scaffold and review learnings](1-1-initialize-dockerized-python-mcp-server-scaffold.md)
- [Pydantic Settings documentation](https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/)
- [Pydantic Settings API documentation](https://pydantic.dev/docs/validation/latest/api/pydantic_settings/)
- [pydantic-settings on PyPI](https://pypi.org/project/pydantic-settings/)
- [PyYAML documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)
- [PyYAML on PyPI](https://pypi.org/project/PyYAML/)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- 2026-06-21: Added direct dependencies with `.\.venv\Scripts\uv.exe add "pydantic>=2.13,<3.0" "pydantic-settings>=2.14,<3.0" "PyYAML>=6.0.3,<7.0"`.
- 2026-06-21: Upgraded lockfile to `pydantic-settings` 2.14.2 with `.\.venv\Scripts\uv.exe lock --upgrade-package pydantic-settings`.
- 2026-06-21: `.\.venv\Scripts\uv.exe run pytest` passed with 18 tests.
- 2026-06-21: `.\.venv\Scripts\uv.exe run ruff check --no-cache .` passed.
- 2026-06-21: `.\.venv\Scripts\uv.exe run ruff format --check --no-cache .` passed.
- 2026-06-21: `docker --config .\.docker-config build --tag geoserver-mcp:dev .` passed.
- 2026-06-21: Smoke checks passed for `geoserver-mcp --version` and MCP app construction without a config file.
- 2026-06-21: Code review patches applied for credential-bearing URLs, path-reference semantics, empty env secrets, duplicate YAML keys, invalid UTF-8, immutable instance collections, env reference validation, redaction coverage, and no-network test guard.
- 2026-06-21: `.\.venv\Scripts\uv.exe run pytest` passed with 28 tests.
- 2026-06-21: `.\.venv\Scripts\uv.exe run ruff check .` passed.
- 2026-06-21: `.\.venv\Scripts\uv.exe run ruff format --check .` passed.
- 2026-06-21: `git diff --check` passed with the existing `.gitignore` LF-to-CRLF warning.
- 2026-06-21: `docker build -t geoserver-mcp:story-1-2-review .` passed.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added typed Pydantic config models for multi-instance GeoServer configuration with HTTP/HTTPS URL validation, duplicate-ID validation, basic-auth env references, and optional Data Directory path references.
- Added safe YAML config loading with project-owned config errors for missing files, parse failures, schema errors, and validation errors.
- Added redaction-safe environment secret resolution that returns runtime credential objects without exposing username/password values through string representations.
- Added security redaction helpers for known secret values and credential-bearing keys.
- Added example config/env files and README configuration guidance.
- Added focused tests for config loading, validation failures, secret resolution, redaction, and existing scaffold behavior.
- Resolved all Story 1.2 code review findings and moved the story to done.

### File List

- _bmad-output/implementation-artifacts/1-2-load-multi-instance-configuration-and-secret-references.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- README.md
- pyproject.toml
- uv.lock
- examples/geoserver-mcp.yaml
- examples/geoserver-mcp.env.example
- src/geoserver_mcp/config/__init__.py
- src/geoserver_mcp/config/errors.py
- src/geoserver_mcp/config/loader.py
- src/geoserver_mcp/config/models.py
- src/geoserver_mcp/config/secrets.py
- src/geoserver_mcp/security/__init__.py
- src/geoserver_mcp/security/redaction.py
- tests/unit/test_config_loader.py
- tests/unit/test_secret_resolution.py
- tests/unit/test_redaction.py

### Change Log

- 2026-06-21: Created Story 1.2 and marked it ready for development.
- 2026-06-21: Implemented Story 1.2 config loading, env secret resolution, redaction, docs, examples, and tests; moved story to review.
- 2026-06-21: Applied all accepted code review patches, reran quality gates, and marked Story 1.2 done.
