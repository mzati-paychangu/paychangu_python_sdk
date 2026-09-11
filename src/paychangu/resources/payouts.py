"""Payout resources (mobile money and bank)."""

from __future__ import annotations

from typing import Any, Optional, Union

from .._http import HttpClient
from .._utils import model_to_dict, omit_none, stringify_amount
from ..models.payout import BankPayout, MobileMoneyPayout


class PayoutsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def momo_operators(self) -> Any:
        """List MoMo operators available for payouts via ``GET /mobile-money``."""
        return self._http.get("/mobile-money")

    def initiate_momo(
        self,
        payout: Optional[Union[MobileMoneyPayout, dict[str, Any]]] = None,
        *,
        mobile: Optional[str] = None,
        mobile_money_operator_ref_id: Optional[str] = None,
        amount: Optional[Union[int, float, str]] = None,
        charge_id: Optional[str] = None,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        transaction_status: Optional[str] = None,
    ) -> Any:
        """Send a MoMo payout via ``POST /mobile-money/payouts/initialize``."""
        if payout is not None:
            payload = model_to_dict(payout) if not isinstance(payout, dict) else omit_none(payout)
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
                    "transaction_status": transaction_status,
                }
            )
        if "amount" in payload and not isinstance(payload["amount"], str):
            payload["amount"] = stringify_amount(payload["amount"])
        return self._http.post("/mobile-money/payouts/initialize", json=payload)

    def momo_details(self, charge_id: str) -> Any:
        """Get MoMo payout details via ``GET /mobile-money/payments/{charge_id}/details``."""
        return self._http.get(f"/mobile-money/payments/{charge_id}/details")

    def banks(self, currency: str = "MWK") -> Any:
        """List supported banks via ``GET /direct-charge/payouts/supported-banks``."""
        return self._http.get(
            "/direct-charge/payouts/supported-banks",
            params={"currency": currency},
        )

    def initiate_bank(
        self,
        payout: Optional[Union[BankPayout, dict[str, Any]]] = None,
        *,
        bank_uuid: Optional[str] = None,
        amount: Optional[Union[int, float, str]] = None,
        charge_id: Optional[str] = None,
        bank_account_name: Optional[str] = None,
        bank_account_number: Optional[str] = None,
        payout_method: str = "bank_transfer",
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> Any:
        """Send a bank payout via ``POST /direct-charge/payouts/initialize``."""
        if payout is not None:
            payload = model_to_dict(payout) if not isinstance(payout, dict) else omit_none(payout)
        else:
            required = [bank_uuid, amount is not None, charge_id, bank_account_name, bank_account_number]
            if not all(required):
                raise ValueError(
                    "bank_uuid, amount, charge_id, bank_account_name, and "
                    "bank_account_number are required"
                )
            payload = omit_none(
                {
                    "payout_method": payout_method,
                    "bank_uuid": bank_uuid,
                    "amount": stringify_amount(amount),
                    "charge_id": charge_id,
                    "bank_account_name": bank_account_name,
                    "bank_account_number": bank_account_number,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                }
            )
        if "amount" in payload and not isinstance(payload["amount"], str):
            payload["amount"] = stringify_amount(payload["amount"])
        return self._http.post("/direct-charge/payouts/initialize", json=payload)

    def bank_details(self, charge_id: str) -> Any:
        """Get a single bank payout via ``GET /direct-charge/payouts/{charge_id}/details``."""
        return self._http.get(f"/direct-charge/payouts/{charge_id}/details")

    def list_bank_payouts(self) -> Any:
        """List bank payouts via ``GET /direct-charge/payouts``."""
        return self._http.get("/direct-charge/payouts")
