from __future__ import annotations

import socket

import pytest

from geoserver_mcp.config import (
    ConfigFileNotFoundError,
    ConfigParseError,
    ConfigValidationError,
    load_config,
)


def test_loads_valid_multi_instance_config(tmp_path) -> None:
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
    data_directory: /mnt/geoserver-prod-data
  - id: staging
    base_url: https://staging-geoserver.example.com/geoserver
    auth:
      type: basic
      username_env: GEOSERVER_STAGING_USER
      password_env: GEOSERVER_STAGING_PASSWORD
""",
        encoding="utf-8",
    )

    config = load_config(config_file)

    assert [instance.id for instance in config.instances] == ["production", "staging"]
    assert str(config.instances[0].base_url) == "https://geoserver.example.com/geoserver"
    assert config.instances[0].auth.password_env == "GEOSERVER_PROD_PASSWORD"
    assert config.instances[0].data_directory == "/mnt/geoserver-prod-data"
    assert not hasattr(config.instances, "append")


def test_duplicate_instance_ids_fail_with_actionable_error(tmp_path) -> None:
    config_file = tmp_path / "geoserver-mcp.yaml"
    config_file.write_text(
        """
instances:
  - id: duplicate
    base_url: https://first.example.com/geoserver
    auth:
      type: basic
      username_env: FIRST_USER
      password_env: FIRST_PASSWORD
  - id: duplicate
    base_url: https://second.example.com/geoserver
    auth:
      type: basic
      username_env: SECOND_USER
      password_env: SECOND_PASSWORD
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigValidationError) as exc_info:
        load_config(config_file)

    assert "duplicate instance id(s): duplicate" in str(exc_info.value)


def test_missing_required_fields_fail_validation(tmp_path) -> None:
    config_file = tmp_path / "geoserver-mcp.yaml"
    config_file.write_text(
        """
instances:
  - id: production
    auth:
      type: basic
      username_env: GEOSERVER_PROD_USER
      password_env: GEOSERVER_PROD_PASSWORD
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigValidationError) as exc_info:
        load_config(config_file)

    assert "base_url: Field required" in str(exc_info.value)


def test_invalid_base_url_scheme_fails_validation(tmp_path) -> None:
    config_file = tmp_path / "geoserver-mcp.yaml"
    config_file.write_text(
        """
instances:
  - id: production
    base_url: ftp://geoserver.example.com/geoserver
    auth:
      type: basic
      username_env: GEOSERVER_PROD_USER
      password_env: GEOSERVER_PROD_PASSWORD
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigValidationError) as exc_info:
        load_config(config_file)

    assert "URL scheme should be 'http' or 'https'" in str(exc_info.value)


@pytest.mark.parametrize(
    "base_url, expected_message",
    [
        (
            "https://operator:secret@geoserver.example.com/geoserver",
            "base_url must not include username or password",
        ),
        (
            "https://geoserver.example.com/geoserver?token=secret",
            "base_url must not include query string or fragment",
        ),
        (
            "https://geoserver.example.com/geoserver#secret",
            "base_url must not include query string or fragment",
        ),
    ],
)
def test_credential_bearing_base_urls_fail_validation(
    tmp_path,
    base_url: str,
    expected_message: str,
) -> None:
    config_file = tmp_path / "geoserver-mcp.yaml"
    config_file.write_text(
        f"""
instances:
  - id: production
    base_url: {base_url}
    auth:
      type: basic
      username_env: GEOSERVER_PROD_USER
      password_env: GEOSERVER_PROD_PASSWORD
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigValidationError) as exc_info:
        load_config(config_file)

    assert expected_message in str(exc_info.value)
    assert "operator:secret" not in str(exc_info.value)
    assert "token=secret" not in str(exc_info.value)


@pytest.mark.parametrize(
    "username_env, password_env, expected_message",
    [
        ("GEOSERVER_PROD_USER\\nINJECTED", "GEOSERVER_PROD_PASSWORD", "must match"),
        ("GEOSERVER_PROD_USER", "GEOSERVER_PROD_USER", "must reference different variables"),
    ],
)
def test_invalid_auth_secret_references_fail_validation(
    tmp_path,
    username_env: str,
    password_env: str,
    expected_message: str,
) -> None:
    config_file = tmp_path / "geoserver-mcp.yaml"
    config_file.write_text(
        f"""
instances:
  - id: production
    base_url: https://geoserver.example.com/geoserver
    auth:
      type: basic
      username_env: "{username_env}"
      password_env: {password_env}
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigValidationError) as exc_info:
        load_config(config_file)

    assert expected_message in str(exc_info.value)


def test_yaml_parse_errors_are_project_owned(tmp_path) -> None:
    config_file = tmp_path / "geoserver-mcp.yaml"
    config_file.write_text("instances: [", encoding="utf-8")

    with pytest.raises(ConfigParseError):
        load_config(config_file)


def test_duplicate_yaml_keys_are_parse_errors(tmp_path) -> None:
    config_file = tmp_path / "geoserver-mcp.yaml"
    config_file.write_text(
        """
instances:
  - id: production
    id: shadow
    base_url: https://geoserver.example.com/geoserver
    auth:
      type: basic
      username_env: GEOSERVER_PROD_USER
      password_env: GEOSERVER_PROD_PASSWORD
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigParseError) as exc_info:
        load_config(config_file)

    assert "duplicate key" in str(exc_info.value)


def test_invalid_utf8_parse_errors_are_project_owned(tmp_path) -> None:
    config_file = tmp_path / "geoserver-mcp.yaml"
    config_file.write_bytes(b"\xff\xfe\x00")

    with pytest.raises(ConfigParseError) as exc_info:
        load_config(config_file)

    assert "not valid UTF-8" in str(exc_info.value)


def test_non_mapping_root_fails_validation(tmp_path) -> None:
    config_file = tmp_path / "geoserver-mcp.yaml"
    config_file.write_text("- not-a-mapping", encoding="utf-8")

    with pytest.raises(ConfigValidationError) as exc_info:
        load_config(config_file)

    assert "configuration root must be a mapping" in str(exc_info.value)


def test_missing_config_file_is_project_owned(tmp_path) -> None:
    with pytest.raises(ConfigFileNotFoundError):
        load_config(tmp_path / "missing.yaml")


def test_config_loading_has_no_network_side_effects(tmp_path, monkeypatch) -> None:
    def fail_network_call(*args: object, **kwargs: object) -> None:
        raise AssertionError("network call attempted")

    monkeypatch.setattr(socket, "create_connection", fail_network_call)
    monkeypatch.setattr(socket, "getaddrinfo", fail_network_call)

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

    assert config.instances[0].id == "production"
