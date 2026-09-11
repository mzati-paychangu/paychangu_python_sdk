"""Request models for US virtual accounts and Connect."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .._utils import dataclass_payload


@dataclass
class VirtualCustomer:
    """Payload for creating or updating a virtual-account customer."""

    email: str
    first_name: str
    last_name: str

    def to_dict(self) -> dict[str, Any]:
        return dataclass_payload(self)


@dataclass
class ConnectAuthorizeParams:
    """Query parameters for ``POST /connect/authorize-link``."""

    client_id: str
    redirect_uri: str
    mode: str
    scope: Optional[str] = "payments:write payments:read"
    wh_url: Optional[str] = None
    wh_secret: Optional[str] = None

    def to_params(self) -> dict[str, Any]:
        return dataclass_payload(self)
