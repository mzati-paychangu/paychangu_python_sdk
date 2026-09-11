"""Request models for direct charges (MoMo and bank transfer)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Union

from .._utils import dataclass_payload, stringify_amount


@dataclass
class MobileMoneyCharge:
    """Payload for ``POST /mobile-money/payments/initialize``."""

    mobile: str
    mobile_money_operator_ref_id: str
    amount: Union[int, float, str]
    charge_id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        data = dataclass_payload(self)
        data["amount"] = stringify_amount(self.amount)
        return data


@dataclass
class BankTransferCharge:
    """Payload for ``POST /direct-charge/payments/initialize``."""

    amount: Union[int, float, str]
    charge_id: str
    currency: str = "MWK"
    payment_method: str = "mobile_bank_transfer"
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    mobile: Optional[str] = None
    create_permanent_account: Optional[bool] = None

    def to_dict(self) -> dict[str, Any]:
        data = dataclass_payload(self)
        data["amount"] = stringify_amount(self.amount)
        return data
