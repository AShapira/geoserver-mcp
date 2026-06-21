from __future__ import annotations

import pytest

from geoserver_mcp.config import load_config, resolve_runtime_config
from geoserver_mcp.config.secrets import SecretResolutionError


def test_resolves_env_secret_references_without_exposing_values(tmp_path) -> None:
    config_file = tmp_path / "geoserver-mcp.yaml"
    config_file.write_text(
        """
instances:
  - id: production
    base_url: https://geoserver.example.com/geoserver
    auth:
      type: basic
      username_env: GEOSERVER_PROD_USER
      password_env: GEOSERVER_PROD_PASSWORD
""",
        encoding="utf-8",
    )
    config = load_config(config_file)

    runtime_config = resolve_runtime_config(
        config,
        {
            "GEOSERVER_PROD_USER": "operator-user",
            "GEOSERVER_PROD_PASSWORD": "operator-password",
        },
    )

    credentials = runtime_config.instances[0].credentials
    assert credentials.as_basic_auth_tuple() == ("operator-user", "operator-password")
    rendered = f"{runtime_config!r} {credentials!r} {credentials}"
    assert "operator-user" not in rendered
    assert "operator-password" not in rendered
    assert "[REDACTED]" in rendered


def test_missing_env_secret_reports_reference_name_without_value(tmp_path) -> None:
    config_file = tmp_path / "geoserver-mcp.yaml"
    config_file.write_text(
        """
instances:
  - id: production
    base_url: https://geoserver.example.com/geoserver
    auth:
      type: basic
      username_env: GEOSERVER_PROD_USER
      password_env: GEOSERVER_PROD_PASSWORD
""",
        encoding="utf-8",
    )
    config = load_config(config_file)

    with pytest.raises(SecretResolutionError) as exc_info:
        resolve_runtime_config(config, {"GEOSERVER_PROD_USER": "operator-user"})

    message = str(exc_info.value)
    assert "GEOSERVER_PROD_PASSWORD" in message
    assert "operator-user" not in message


def test_empty_env_secret_is_rejected_without_exposing_values(tmp_path) -> None:
    config_file = tmp_path / "geoserver-mcp.yaml"
    config_file.write_text(
        """
instances:
  - id: production
    base_url: https://geoserver.example.com/geoserver
    auth:
      type: basic
      username_env: GEOSERVER_PROD_USER
      password_env: GEOSERVER_PROD_PASSWORD
""",
        encoding="utf-8",
    )
    config = load_config(config_file)

    with pytest.raises(SecretResolutionError) as exc_info:
        resolve_runtime_config(
            config,
            {
                "GEOSERVER_PROD_USER": "operator-user",
                "GEOSERVER_PROD_PASSWORD": "",
            },
        )

    message = str(exc_info.value)
    assert "GEOSERVER_PROD_PASSWORD" in message
    assert "operator-user" not in message
