"""PayChangu Connect resources."""

from __future__ import annotations

from typing import Any, Optional, Union

from .._http import HttpClient
from .._utils import omit_none
from ..models.virtual_account import ConnectAuthorizeParams


class ConnectResource:
    """
    PayChangu Connect (OAuth-style) helpers.

    Use Connect when a SaaS product should accept payments on behalf of
    merchants without holding their funds or sharing API keys.
    """

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def authorize_link(
        self,
        params: Optional[Union[ConnectAuthorizeParams, dict[str, Any]]] = None,
        *,
        client_id: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        mode: Optional[str] = None,
        scope: Optional[str] = "payments:write payments:read",
        wh_url: Optional[str] = None,
        wh_secret: Optional[str] = None,
    ) -> Any:
        """
        Generate a Connect authorization URL via ``POST /connect/authorize-link``.

        Redirect the merchant to the returned link so they can grant permissions.
        """
        if params is not None:
            query = params.to_params() if isinstance(params, ConnectAuthorizeParams) else omit_none(params)
            mode_value = query.get("mode")
            if mode_value is not None and mode_value not in ("live", "test"):
                raise ValueError("mode must be 'live' or 'test'")
        else:
            if not client_id or not redirect_uri or not mode:
                raise ValueError("client_id, redirect_uri, and mode are required")
            if mode not in ("live", "test"):
                raise ValueError("mode must be 'live' or 'test'")
            query = omit_none(
                {
                    "client_id": client_id,
                    "redirect_uri": redirect_uri,
                    "mode": mode,
                    "scope": scope,
                    "wh_url": wh_url,
                    "wh_secret": wh_secret,
                }
            )
        return self._http.post("/connect/authorize-link", params=query)

    def user(self, access_token: Optional[str] = None) -> Any:
        """
        Retrieve connected-user info via ``GET /connect/user``.

        Pass ``access_token`` as a query parameter when not authenticating with
        that token as the Bearer credential.
        """
        params = {"access_token": access_token} if access_token else None
        return self._http.get("/connect/user", params=params)

    def revoke(self, token: str) -> Any:
        """
        Revoke a Connect access token via ``POST /connect/revoke``.

        Note: the public OpenAPI listing currently uses a placeholder path; this
        SDK uses ``/connect/revoke`` to match the other Connect routes. Merchants
        can also revoke apps from the PayChangu dashboard.
        """
        if not token:
            raise ValueError("token is required")
        return self._http.post("/connect/revoke", params={"token": token})
