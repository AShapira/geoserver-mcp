from __future__ import annotations

import re
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator

ENV_VAR_PATTERN = r"^[A-Za-z_][A-Za-z0-9_]*$"


class BasicAuthReference(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    type: Literal["basic"] = "basic"
    username_env: str = Field(min_length=1)
    password_env: str = Field(min_length=1)

    @field_validator("username_env", "password_env")
    @classmethod
    def validate_env_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("environment variable name must not be empty")
        if not re.fullmatch(ENV_VAR_PATTERN, value):
            raise ValueError("environment variable name must match [A-Za-z_][A-Za-z0-9_]*")
        return value

    @model_validator(mode="after")
    def validate_distinct_secret_references(self) -> Self:
        if self.username_env == self.password_env:
            raise ValueError("username_env and password_env must reference different variables")
        return self


class GeoServerInstanceConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(min_length=1, pattern=r"^[A-Za-z0-9_-]+$")
    base_url: HttpUrl
    auth: BasicAuthReference
    data_directory: str | None = None

    @field_validator("base_url")
    @classmethod
    def reject_credential_bearing_urls(cls, value: HttpUrl) -> HttpUrl:
        if value.username or value.password:
            raise ValueError("base_url must not include username or password")
        if value.query or value.fragment:
            raise ValueError("base_url must not include query string or fragment")
        return value

    @field_validator("data_directory", mode="before")
    @classmethod
    def empty_data_directory_is_not_configured(cls, value: object) -> object:
        if value == "":
            return None
        return value

    @field_validator("data_directory")
    @classmethod
    def validate_data_directory_reference(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("data_directory must not be blank")
        return value


class AppConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    instances: tuple[GeoServerInstanceConfig, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_instance_ids(self) -> Self:
        seen: set[str] = set()
        duplicates: list[str] = []
        for instance in self.instances:
            if instance.id in seen and instance.id not in duplicates:
                duplicates.append(instance.id)
            seen.add(instance.id)
        if duplicates:
            duplicate_list = ", ".join(sorted(duplicates))
            raise ValueError(f"duplicate instance id(s): {duplicate_list}")
        return self
