from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

from pydantic import SecretStr

from geoserver_mcp.config.errors import ConfigError
from geoserver_mcp.config.models import AppConfig, BasicAuthReference, GeoServerInstanceConfig


class SecretResolutionError(ConfigError):
    code = "secret_resolution_error"


@dataclass(frozen=True)
class BasicCredentials:
    username: SecretStr
    password: SecretStr

    def as_basic_auth_tuple(self) -> tuple[str, str]:
        return (self.username.get_secret_value(), self.password.get_secret_value())

    def __repr__(self) -> str:
        return "BasicCredentials(username='[REDACTED]', password='[REDACTED]')"

    __str__ = __repr__


@dataclass(frozen=True)
class RuntimeInstanceConfig:
    id: str
    base_url: str
    data_directory: str | None
    credentials: BasicCredentials

    def __repr__(self) -> str:
        return (
            "RuntimeInstanceConfig("
            f"id={self.id!r}, base_url={self.base_url!r}, "
            f"data_directory={self.data_directory!r}, credentials=[REDACTED])"
        )

    __str__ = __repr__


@dataclass(frozen=True)
class RuntimeConfig:
    instances: tuple[RuntimeInstanceConfig, ...]


def resolve_runtime_config(
    config: AppConfig,
    environ: Mapping[str, str] | None = None,
) -> RuntimeConfig:
    env = os.environ if environ is None else environ
    return RuntimeConfig(
        instances=tuple(resolve_instance_config(instance, env) for instance in config.instances)
    )


def resolve_instance_config(
    instance: GeoServerInstanceConfig,
    environ: Mapping[str, str] | None = None,
) -> RuntimeInstanceConfig:
    env = os.environ if environ is None else environ
    return RuntimeInstanceConfig(
        id=instance.id,
        base_url=str(instance.base_url),
        data_directory=instance.data_directory,
        credentials=resolve_basic_auth(instance.auth, env),
    )


def resolve_basic_auth(
    auth: BasicAuthReference,
    environ: Mapping[str, str] | None = None,
) -> BasicCredentials:
    env = os.environ if environ is None else environ
    missing = [name for name in (auth.username_env, auth.password_env) if not env.get(name)]
    if missing:
        missing_names = ", ".join(sorted(missing))
        raise SecretResolutionError(
            f"missing or empty secret environment variable(s): {missing_names}"
        )
    return BasicCredentials(
        username=SecretStr(env[auth.username_env]),
        password=SecretStr(env[auth.password_env]),
    )
