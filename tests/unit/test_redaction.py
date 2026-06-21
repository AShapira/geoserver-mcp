from __future__ import annotations

from geoserver_mcp.security import REDACTION, redact_text, redact_value


def test_redact_text_replaces_known_secret_values() -> None:
    message = "login failed for operator-user with password operator-password"

    redacted = redact_text(message, ["operator-user", "operator-password"])

    assert redacted == f"login failed for {REDACTION} with password {REDACTION}"


def test_redact_text_replaces_longer_overlapping_secrets_first() -> None:
    message = "token values abc and abc123 were observed"

    redacted = redact_text(message, ["abc", "abc123"])

    assert redacted == f"token values {REDACTION} and {REDACTION} were observed"


def test_redact_value_masks_credential_keys_but_preserves_env_reference_names() -> None:
    value = {
        "accessKey": "access-key-value",
        "api_key": "api-key-value",
        "clientSecret": "client-secret-value",
        "username": "operator-user",
        "password": "operator-password",
        "username_env": "GEOSERVER_PROD_USER",
        "password_env": "GEOSERVER_PROD_PASSWORD",
        "nested": {"api_token": "token-value"},
    }

    redacted = redact_value(value)

    assert redacted["accessKey"] == REDACTION
    assert redacted["api_key"] == REDACTION
    assert redacted["clientSecret"] == REDACTION
    assert redacted["username"] == REDACTION
    assert redacted["password"] == REDACTION
    assert redacted["username_env"] == "GEOSERVER_PROD_USER"
    assert redacted["password_env"] == "GEOSERVER_PROD_PASSWORD"
    assert redacted["nested"]["api_token"] == REDACTION


def test_redact_value_recursively_replaces_known_secret_text() -> None:
    value = {"detail": ["operator-password appeared in an adapter error"]}

    redacted = redact_value(value, ["operator-password"])

    assert redacted == {"detail": [f"{REDACTION} appeared in an adapter error"]}
