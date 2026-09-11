"""Hosted checkout (Level) payment resources."""

from __future__ import annotations

from typing import Any, Union

from .._http import HttpClient
from .._utils import model_to_dict
from ..models.payment import Payment


class PaymentsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def initiate(self, payment: Union[Payment, dict[str, Any]]) -> Any:
        """Create a hosted checkout session via ``POST /payment``."""
        payload = model_to_dict(payment) if not isinstance(payment, dict) else {
            k: v for k, v in payment.items() if v is not None
        }
        if "amount" in payload and not isinstance(payload["amount"], str):
            from .._utils import stringify_amount

            payload["amount"] = stringify_amount(payload["amount"])
        return self._http.post("/payment", json=payload)

    def verify(self, tx_ref: str) -> Any:
        """Verify a transaction via ``GET /verify-payment/{tx_ref}``."""
        return self._http.get(f"/verify-payment/{tx_ref}")
