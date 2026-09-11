"""Direct charge resources (mobile money and bank transfer)."""

from __future__ import annotations

from typing import Any, Optional, Union

from .._http import HttpClient
from .._utils import model_to_dict, omit_none, stringify_amount
from ..models.charge import BankTransferCharge, MobileMoneyCharge


class DirectChargeResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def operators(self) -> Any:
        """List supported mobile money operators via ``GET /mobile-money``."""
        return self._http.get("/mobile-money")

    def initialize(
        self,
        charge: Optional[Union[MobileMoneyCharge, dict[str, Any]]] = None,
        *,
        mobile: Optional[str] = None,
        mobile_money_operator_ref_id: Optional[str] = None,
        amount: Optional[Union[int, float, str]] = None,
        charge_id: Optional[str] = None,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> Any:
        """Initialize a MoMo direct charge via ``POST /mobile-money/payments/initialize``."""
        if charge is not None:
            payload = model_to_dict(charge) if not isinstance(charge, dict) else omit_none(charge)
        else:
            if not all([mobile, mobile_money_operator_ref_id, amount is not None, charge_id]):
                raise ValueError(
                    "mobile, mobile_money_operator_ref_id, amount, and charge_id are required"
                )
            payload = omit_none(
                {
                    "mobile": mobile,
                    "mobile_money_operator_ref_id": mobile_money_operator_ref_id,
                    "amount": stringify_amount(amount),
                    "charge_id": charge_id,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                }
            )
        if "amount" in payload and not isinstance(payload["amount"], str):
            payload["amount"] = stringify_amount(payload["amount"])
        return self._http.post("/mobile-money/payments/initialize", json=payload)

    def verify(self, charge_id: str) -> Any:
        """Verify a MoMo direct charge via ``GET /mobile-money/payments/{charge_id}/verify``."""
        return self._http.get(f"/mobile-money/payments/{charge_id}/verify")

    def details(self, charge_id: str) -> Any:
        """Get MoMo charge details via ``GET /mobile-money/payments/{charge_id}/details``."""
        return self._http.get(f"/mobile-money/payments/{charge_id}/details")

    def initialize_bank_transfer(
        self,
        charge: Optional[Union[BankTransferCharge, dict[str, Any]]] = None,
        *,
        amount: Optional[Union[int, float, str]] = None,
        charge_id: Optional[str] = None,
        currency: str = "MWK",
        payment_method: str = "mobile_bank_transfer",
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        mobile: Optional[str] = None,
        create_permanent_account: Optional[bool] = None,
    ) -> Any:
        """Initialize a bank-transfer charge via ``POST /direct-charge/payments/initialize``."""
        if charge is not None:
            payload = model_to_dict(charge) if not isinstance(charge, dict) else omit_none(charge)
        else:
            if amount is None or not charge_id:
                raise ValueError("amount and charge_id are required")
            payload = omit_none(
                {
                    "amount": stringify_amount(amount),
                    "currency": currency,
                    "payment_method": payment_method,
                    "charge_id": charge_id,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "mobile": mobile,
                    "create_permanent_account": create_permanent_account,
                }
            )
        if "amount" in payload and not isinstance(payload["amount"], str):
            payload["amount"] = stringify_amount(payload["amount"])
        return self._http.post("/direct-charge/payments/initialize", json=payload)

    def bank_transfer_details(self, charge_id: str) -> Any:
        """Get bank-transfer charge details via ``GET /direct-charge/transactions/{charge_id}/details``."""
        return self._http.get(f"/direct-charge/transactions/{charge_id}/details")
