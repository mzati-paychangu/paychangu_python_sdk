"""HTTP transport for the PayChangu SDK."""

from __future__ import annotations

from typing import Any, Mapping, Optional

import requests

from .exceptions import APIError, NetworkError, raise_for_api_status

DEFAULT_TIMEOUT = 30.0
DEFAULT_BASE_URL = "https://api.paychangu.com"

Params = Optional[Mapping[str, Any]]
Payload = Optional[Mapping[str, Any]]


class HttpClient:
    """Thin wrapper around ``requests.Session`` with auth, timeouts, and errors."""

    def __init__(
        self,
        secret_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        session: Optional[requests.Session] = None,
    ) -> None:
        if not secret_key:
            raise ValueError("secret_key is required")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = session or requests.Session()
        self._session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {secret_key}",
            }
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Params = None,
        json: Payload = None,
    ) -> Any:
        url = f"{self.base_url}{path}" if path.startswith("/") else f"{self.base_url}/{path}"
        try:
            response = self._session.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json,
                timeout=self.timeout,
            )
        except requests.exceptions.RequestException as exc:
            raise NetworkError(f"Request failed: {exc}") from exc

        return self._parse_response(response)

    def get(self, path: str, *, params: Params = None) -> Any:
        return self.request("GET", path, params=params)

    def post(self, path: str, *, json: Payload = None, params: Params = None) -> Any:
        return self.request("POST", path, json=json, params=params)

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    @staticmethod
    def _parse_response(response: requests.Response) -> Any:
        try:
            body: Any = response.json() if response.content else None
        except ValueError as exc:
            if not response.ok:
                raise APIError(
                    response.text or f"HTTP {response.status_code}",
                    status_code=response.status_code,
                    body=response.text,
                ) from exc
            raise APIError(
                "Invalid JSON response from the API",
                status_code=response.status_code,
                body=response.text,
            ) from exc

        if not response.ok:
            raise_for_api_status(response.status_code, body)

        return body
