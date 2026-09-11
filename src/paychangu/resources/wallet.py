"""Wallet / balance resources."""

from __future__ import annotations

from typing import Any, Optional

from .._http import HttpClient


class WalletResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def balance(self, currency: Optional[str] = "MWK") -> Any:
        """Retrieve wallet balance via ``GET /wallet-balance``."""
        params = {"currency": currency} if currency else None
        return self._http.get("/wallet-balance", params=params)
