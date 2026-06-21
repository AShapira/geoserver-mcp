"""Application configuration loading and secret resolution."""

from geoserver_mcp.config.errors import (
    ConfigError,
    ConfigFileNotFoundError,
    ConfigParseError,
    ConfigValidationError,
)
from geoserver_mcp.config.loader import load_config, parse_config
from geoserver_mcp.config.models import AppConfig, BasicAuthReference, GeoServerInstanceConfig
from geoserver_mcp.config.secrets import (
    BasicCredentials,
    RuntimeConfig,
    RuntimeInstanceConfig,
    SecretResolutionError,
    resolve_basic_auth,
    resolve_instance_config,
    resolve_runtime_config,
)

__all__ = [
    "AppConfig",
    "BasicAuthReference",
    "BasicCredentials",
    "ConfigError",
    "ConfigFileNotFoundError",
    "ConfigParseError",
    "ConfigValidationError",
    "GeoServerInstanceConfig",
    "RuntimeConfig",
    "RuntimeInstanceConfig",
    "SecretResolutionError",
    "load_config",
    "parse_config",
    "resolve_basic_auth",
    "resolve_instance_config",
    "resolve_runtime_config",
]
