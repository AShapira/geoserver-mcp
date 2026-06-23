from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal
from urllib.parse import quote, unquote, urlsplit

import httpx

from geoserver_mcp.config import RuntimeInstanceConfig
from geoserver_mcp.domain import ReasonCode
from geoserver_mcp.security import redact_text, redact_value

REST_VERSION_ENDPOINT = "rest/about/version.json"
DEFAULT_TIMEOUT_SECONDS = 5.0
STORE_ENDPOINTS = {
    "data_stores": "datastores",
    "coverage_stores": "coveragestores",
    "wms_stores": "wmsstores",
}


@dataclass(frozen=True)
class GeoServerRestResult:
    status: Literal["success", "failed"]
    data: Mapping[str, Any] | None = None
    reason_code: ReasonCode | None = None
    message: str = ""
    status_code: int | None = None
    url: str | None = None

    @property
    def succeeded(self) -> bool:
        return self.status == "success"

    def __repr__(self) -> str:
        return (
            "GeoServerRestResult("
            f"status={self.status!r}, reason_code={self.reason_code!r}, "
            f"status_code={self.status_code!r}, url={self.url!r})"
        )

    __str__ = __repr__


class GeoServerRestClient:
    def __init__(
        self,
        instance: RuntimeInstanceConfig,
        *,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        follow_redirects: bool = False,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.instance = instance
        self.timeout_seconds = timeout_seconds
        self.follow_redirects = follow_redirects
        self._transport = transport
        self._base_url = httpx.URL(instance.base_url)

    async def get_connectivity_metadata(self) -> GeoServerRestResult:
        return await self.get_json(REST_VERSION_ENDPOINT)

    async def list_workspaces(self) -> GeoServerRestResult:
        return await self.get_json("rest/workspaces.json")

    async def list_stores(self, workspace: str, store_type: str) -> GeoServerRestResult:
        endpoint = STORE_ENDPOINTS.get(store_type)
        if endpoint is None:
            return self._failure(
                ReasonCode.UNSUPPORTED_ENDPOINT,
                "unsupported GeoServer store type",
            )
        safe_workspace = quote(workspace, safe="")
        return await self.get_json(f"rest/workspaces/{safe_workspace}/{endpoint}.json")

    async def list_layers(self) -> GeoServerRestResult:
        return await self.get_json("rest/layers.json")

    async def list_layer_groups(self) -> GeoServerRestResult:
        return await self.get_json("rest/layergroups.json")

    async def get_json(self, target: str) -> GeoServerRestResult:
        target_url = self._build_safe_url(target)
        if target_url is None:
            return self._failure(
                ReasonCode.UNSUPPORTED_ENDPOINT,
                "request target is not a safe relative GeoServer REST endpoint",
            )

        try:
            async with httpx.AsyncClient(
                auth=self.instance.credentials.as_basic_auth_tuple(),
                follow_redirects=self.follow_redirects,
                timeout=httpx.Timeout(self.timeout_seconds),
                transport=self._transport,
            ) as client:
                response = await client.get(target_url)
        except httpx.TimeoutException:
            return self._failure(ReasonCode.NETWORK_ERROR, "GeoServer request timed out")
        except httpx.RequestError:
            return self._failure(ReasonCode.NETWORK_ERROR, "GeoServer request failed")
        except Exception:
            return self._failure(
                ReasonCode.UNKNOWN,
                "unexpected GeoServer REST adapter failure",
            )

        if response.status_code == 401:
            return self._failure(
                ReasonCode.AUTH_FAILED,
                "GeoServer authentication failed",
                status_code=response.status_code,
                url=str(response.url),
            )
        if response.status_code == 403:
            return self._failure(
                ReasonCode.FORBIDDEN,
                "GeoServer request was forbidden",
                status_code=response.status_code,
                url=str(response.url),
            )
        if response.status_code == 404:
            return self._failure(
                ReasonCode.NOT_FOUND,
                "GeoServer endpoint was not found",
                status_code=response.status_code,
                url=str(response.url),
            )
        if 300 <= response.status_code < 400:
            return self._failure(
                ReasonCode.UNSUPPORTED_ENDPOINT,
                "GeoServer redirect response was not followed",
                status_code=response.status_code,
                url=str(response.url),
            )
        if response.status_code >= 400:
            return self._failure(
                ReasonCode.UNKNOWN,
                "GeoServer request failed with an unexpected HTTP status",
                status_code=response.status_code,
                url=str(response.url),
            )

        try:
            data = response.json()
        except ValueError:
            return self._failure(
                ReasonCode.PARSE_ERROR,
                "GeoServer response body was not valid JSON",
                status_code=response.status_code,
                url=str(response.url),
            )
        if not isinstance(data, Mapping):
            return self._failure(
                ReasonCode.PARSE_ERROR,
                "GeoServer response JSON was not an object",
                status_code=response.status_code,
                url=str(response.url),
            )

        return GeoServerRestResult(
            status="success",
            data=redact_value(data, self._known_secret_values()),
            status_code=response.status_code,
            url=self._redact(str(response.url)),
        )

    def _build_safe_url(self, target: str) -> httpx.URL | None:
        candidate = target.strip()
        if not candidate:
            return None
        parsed = urlsplit(candidate)
        if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
            return None
        normalized_path = parsed.path.replace("\\", "/")
        if normalized_path.startswith("/"):
            return None
        raw_segments = [segment for segment in normalized_path.split("/") if segment]
        if not raw_segments:
            return None
        safe_segments: list[str] = []
        for segment in raw_segments:
            decoded_segment = unquote(segment)
            if decoded_segment in {".", ".."} or "/" in decoded_segment or "\\" in decoded_segment:
                return None
            safe_segments.append(segment)

        base_path = self._base_url.path.rstrip("/")
        safe_path = (
            f"{base_path}/{'/'.join(safe_segments)}" if base_path else f"/{'/'.join(safe_segments)}"
        )
        safe_url = self._base_url.copy_with(path=safe_path, query=None, fragment=None)
        if (
            safe_url.scheme != self._base_url.scheme
            or safe_url.host != self._base_url.host
            or safe_url.port != self._base_url.port
        ):
            return None
        return safe_url

    def _failure(
        self,
        reason_code: ReasonCode,
        message: str,
        *,
        status_code: int | None = None,
        url: str | None = None,
    ) -> GeoServerRestResult:
        return GeoServerRestResult(
            status="failed",
            reason_code=reason_code,
            message=self._redact(message),
            status_code=status_code,
            url=self._redact(url) if url else None,
        )

    def _redact(self, text: str) -> str:
        return redact_text(text, self._known_secret_values())

    def _known_secret_values(self) -> tuple[str, str]:
        return self.instance.credentials.as_basic_auth_tuple()
