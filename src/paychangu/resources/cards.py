"""Card charge resources."""

from __future__ import annotations

from typing import Any, Optional, Union

from .._http import HttpClient
from .._utils import model_to_dict, omit_none, stringify_amount
from ..models.card import CardCharge


class CardsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def charge(
        self,
        card: Optional[Union[CardCharge, dict[str, Any]]] = None,
        *,
        card_number: Optional[str] = None,
        expiry: Optional[str] = None,
        cvv: Optional[str] = None,
        cardholder_name: Optional[str] = None,
        amount: Optional[Union[int, float, str]] = None,
        currency: Optional[str] = None,
        charge_id: Optional[str] = None,
        redirect_url: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Any:
        """
        Charge a card via ``POST /charge-card/payments``.

        Only use this from a PCI-compliant environment. Prefer hosted checkout
        when you do not need to handle raw card data yourself.
        """
        if card is not None:
            payload = model_to_dict(card) if not isinstance(card, dict) else omit_none(card)
        else:
            required = [
                card_number,
                expiry,
                cvv,
                cardholder_name,
                amount is not None,
                currency,
                charge_id,
                redirect_url,
            ]
            if not all(required):
                raise ValueError(
                    "card_number, expiry, cvv, cardholder_name, amount, currency, "
                    "charge_id, and redirect_url are required"
                )
            payload = omit_none(
                {
                    "card_number": card_number,
                    "expiry": expiry,
                    "cvv": cvv,
                    "cardholder_name": cardholder_name,
                    "amount": stringify_amount(amount),
                    "currency": currency,
                    "charge_id": charge_id,
                    "redirect_url": redirect_url,
                    "email": email,
                }
            )
        if "amount" in payload and not isinstance(payload["amount"], str):
            payload["amount"] = stringify_amount(payload["amount"])
        return self._http.post("/charge-card/payments", json=payload)

    def verify(self, charge_id: str) -> Any:
        """Verify a card charge via ``GET /charge-card/verify/{charge_id}``."""
        return self._http.get(f"/charge-card/verify/{charge_id}")

    def refund(self, charge_id: str) -> Any:
        """Refund a card charge via ``POST /charge-card/refund/{charge_id}``."""
        return self._http.post(f"/charge-card/refund/{charge_id}")
