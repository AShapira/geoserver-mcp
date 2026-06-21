from __future__ import annotations

from enum import StrEnum


class ReasonCode(StrEnum):
    NETWORK_ERROR = "network_error"
    AUTH_FAILED = "auth_failed"
    FORBIDDEN = "forbidden"
    NOT_FOUND = "not_found"
    UNSUPPORTED_ENDPOINT = "unsupported_endpoint"
    DISABLED_SERVICE = "disabled_service"
    PARSE_ERROR = "parse_error"
    MISSING_DATA_DIRECTORY = "missing_data_directory"
    UNREADABLE_DATA_DIRECTORY = "unreadable_data_directory"
    REDACTED = "redacted"
    PARTIAL_RESULT = "partial_result"
    UNKNOWN = "unknown"


class ResponseStatus(StrEnum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
