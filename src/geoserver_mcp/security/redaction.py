from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

REDACTION = "[REDACTED]"
SECRET_FIELD_NAMES = {
    "access_key",
    "api_key",
    "authorization",
    "client_secret",
    "credential",
    "credentials",
    "password",
    "private_key",
    "secret",
    "secret_key",
    "token",
    "username",
}
SECRET_FIELD_SUFFIXES = (
    "_credential",
    "_credentials",
    "_key",
    "_password",
    "_secret",
    "_token",
)


def redact_text(text: str, known_secrets: Sequence[str] = ()) -> str:
    redacted = text
    secrets = sorted((secret for secret in known_secrets if secret), key=len, reverse=True)
    for secret in secrets:
        redacted = redacted.replace(secret, REDACTION)
    return redacted


def redact_value(value: Any, known_secrets: Sequence[str] = ()) -> Any:
    if isinstance(value, str):
        return redact_text(value, known_secrets)
    if isinstance(value, Mapping):
        return {
            key: REDACTION if _is_secret_field(str(key)) else redact_value(item, known_secrets)
            for key, item in value.items()
        }
    if isinstance(value, tuple):
        return tuple(redact_value(item, known_secrets) for item in value)
    if isinstance(value, list):
        return [redact_value(item, known_secrets) for item in value]
    return value


def _is_secret_field(key: str) -> bool:
    normalized = _normalize_field_name(key)
    if normalized.endswith("_env"):
        return False
    return normalized in SECRET_FIELD_NAMES or normalized.endswith(SECRET_FIELD_SUFFIXES)


def _normalize_field_name(key: str) -> str:
    snake_key = re.sub(r"(?<!^)(?=[A-Z])", "_", key)
    return snake_key.replace("-", "_").lower()
