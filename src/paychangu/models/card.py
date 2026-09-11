"""Request models for card charges."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Union

from .._utils import dataclass_payload, stringify_amount


@dataclass
class CardCharge:
    """
    Payload for ``POST /charge-card/payments``.

    Card data must only be handled in a PCI-compliant environment.
    Prefer hosted checkout or tokenization flows when possible.
    """

    card_number: str
    expiry: str
    cvv: str
    cardholder_name: str
    amount: Union[int, float, str]
    currency: str
    charge_id: str
    redirect_url: str
    email: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        data = dataclass_payload(self)
        data["amount"] = stringify_amount(self.amount)
        return data
