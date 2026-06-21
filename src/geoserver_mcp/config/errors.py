from __future__ import annotations

from collections.abc import Iterable

from pydantic import ValidationError

from geoserver_mcp.security.redaction import redact_text


class ConfigError(Exception):
    code = "config_error"

    def __init__(self, message: str, details: Iterable[str] = ()) -> None:
        self.message = message
        self.details = tuple(details)
        super().__init__(str(self))

    def __str__(self) -> str:
        if not self.details:
            return f"{self.code}: {self.message}"
        return f"{self.code}: {self.message}: {'; '.join(self.details)}"

    def to_dict(self) -> dict[str, object]:
        return {"code": self.code, "message": self.message, "details": list(self.details)}


class ConfigFileNotFoundError(ConfigError):
    code = "config_file_not_found"


class ConfigParseError(ConfigError):
    code = "config_parse_error"


class ConfigValidationError(ConfigError):
    code = "config_validation_error"

    @classmethod
    def from_validation_error(
        cls, error: ValidationError, known_secrets: Iterable[str] = ()
    ) -> ConfigValidationError:
        secret_values = tuple(known_secrets)
        details = []
        for item in error.errors(include_url=False):
            location = ".".join(str(part) for part in item["loc"])
            message = redact_text(str(item["msg"]), secret_values)
            details.append(f"{location}: {message}" if location else message)
        return cls("configuration failed validation", details)
