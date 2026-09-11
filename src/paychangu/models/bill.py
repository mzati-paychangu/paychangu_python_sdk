"""Request models for bill payments and airtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Union

from .._utils import dataclass_payload, stringify_amount


@dataclass
class BillPayment:
    """Payload for ``POST /bills/pay``."""

    biller: str
    account: str
    amount: Optional[Union[int, float, str]] = None
    customer_name: Optional[str] = None
    account_type: Optional[str] = None
    reference: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        data = dataclass_payload(self)
        if "amount" in data:
            data["amount"] = stringify_amount(self.amount)
        return data


@dataclass
class BillValidation:
    """Payload for ``POST /bills/validate``."""

    biller: str
    account: str
    account_type: Optional[str] = None
    amount: Optional[Union[int, float, str]] = None

    def to_dict(self) -> dict[str, Any]:
        data = dataclass_payload(self)
        if "amount" in data:
            data["amount"] = stringify_amount(self.amount)
        return data


@dataclass
class AirtimePurchase:
    """Payload for ``POST /bills/buy-airtime``."""

    phone: str
    amount: Union[int, float, str]
    reference: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        data = dataclass_payload(self)
        data["amount"] = stringify_amount(self.amount)
        return data
