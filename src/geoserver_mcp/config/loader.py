from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from geoserver_mcp.config.errors import (
    ConfigFileNotFoundError,
    ConfigParseError,
    ConfigValidationError,
)
from geoserver_mcp.config.models import AppConfig


class _UniqueKeySafeLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(
    loader: _UniqueKeySafeLoader,
    node: yaml.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    seen_keys: set[Any] = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in seen_keys:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        seen_keys.add(key)
    return loader.construct_mapping(node, deep=deep)


_UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def load_config(path: str | Path) -> AppConfig:
    config_path = Path(path)
    if not config_path.is_file():
        raise ConfigFileNotFoundError(f"config file does not exist: {config_path}")

    try:
        with config_path.open("r", encoding="utf-8") as config_file:
            raw_config = yaml.load(config_file, Loader=_UniqueKeySafeLoader)
    except yaml.YAMLError as exc:
        raise ConfigParseError("config file is not valid YAML", [str(exc)]) from exc
    except UnicodeDecodeError as exc:
        raise ConfigParseError("config file is not valid UTF-8", [str(exc)]) from exc
    except OSError as exc:
        raise ConfigParseError(f"config file could not be read: {config_path}", [str(exc)]) from exc

    if raw_config is None:
        raw_config = {}
    if not isinstance(raw_config, dict):
        raise ConfigValidationError("configuration root must be a mapping")

    return parse_config(raw_config)


def parse_config(raw_config: dict[str, Any]) -> AppConfig:
    try:
        return AppConfig.model_validate(raw_config)
    except ValidationError as exc:
        raise ConfigValidationError.from_validation_error(exc) from exc
