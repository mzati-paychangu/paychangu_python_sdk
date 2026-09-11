"""Bill payment and airtime resources."""

from __future__ import annotations

from typing import Any, Optional, Union

from .._http import HttpClient
from .._utils import model_to_dict, omit_none, stringify_amount
from ..models.bill import AirtimePurchase, BillPayment, BillValidation


class BillsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def billers(self) -> Any:
        """List available billers via ``GET /bills/getBillers``."""
        return self._http.get("/bills/getBillers")

    def biller_details(self, biller_id: str) -> Any:
        """Get details for a biller via ``GET /bills/getBillers/{biller_id}``."""
        return self._http.get(f"/bills/getBillers/{biller_id}")

    def validate(
        self,
        bill: Optional[Union[BillValidation, dict[str, Any]]] = None,
        *,
        biller: Optional[str] = None,
        account: Optional[str] = None,
        account_type: Optional[str] = None,
        amount: Optional[Union[int, float, str]] = None,
    ) -> Any:
        """Validate a bill via ``POST /bills/validate``."""
        if bill is not None:
            payload = model_to_dict(bill) if not isinstance(bill, dict) else omit_none(bill)
        else:
            if not biller or not account:
                raise ValueError("biller and account are required")
            payload = omit_none(
                {
                    "biller": biller,
                    "account": account,
                    "account_type": account_type,
                    "amount": stringify_amount(amount) if amount is not None else None,
                }
            )
        if "amount" in payload and not isinstance(payload["amount"], str):
            payload["amount"] = stringify_amount(payload["amount"])
        return self._http.post("/bills/validate", json=payload)

    def pay(
        self,
        bill: Optional[Union[BillPayment, dict[str, Any]]] = None,
        *,
        biller: Optional[str] = None,
        account: Optional[str] = None,
        amount: Optional[Union[int, float, str]] = None,
        customer_name: Optional[str] = None,
        account_type: Optional[str] = None,
        reference: Optional[str] = None,
    ) -> Any:
        """Pay a bill via ``POST /bills/pay``."""
        if bill is not None:
            payload = model_to_dict(bill) if not isinstance(bill, dict) else omit_none(bill)
        else:
            if not biller or not account:
                raise ValueError("biller and account are required")
            payload = omit_none(
                {
                    "biller": biller,
                    "account": account,
                    "amount": stringify_amount(amount) if amount is not None else None,
                    "customer_name": customer_name,
                    "account_type": account_type,
                    "reference": reference,
                }
            )
        if "amount" in payload and not isinstance(payload["amount"], str):
            payload["amount"] = stringify_amount(payload["amount"])
        return self._http.post("/bills/pay", json=payload)

    def buy_airtime(
        self,
        purchase: Optional[Union[AirtimePurchase, dict[str, Any]]] = None,
        *,
        phone: Optional[str] = None,
        amount: Optional[Union[int, float, str]] = None,
        reference: Optional[str] = None,
    ) -> Any:
        """Recharge airtime via ``POST /bills/buy-airtime``."""
        if purchase is not None:
            payload = (
                model_to_dict(purchase) if not isinstance(purchase, dict) else omit_none(purchase)
            )
        else:
            if not phone or amount is None:
                raise ValueError("phone and amount are required")
            payload = omit_none(
                {
                    "phone": phone,
                    "amount": stringify_amount(amount),
                    "reference": reference,
                }
            )
        if "amount" in payload and not isinstance(payload["amount"], str):
            payload["amount"] = stringify_amount(payload["amount"])
        return self._http.post("/bills/buy-airtime", json=payload)

    def details(self, reference: str) -> Any:
        """Get bill transaction details via ``GET /bills/getTransactions/{reference}``."""
        return self._http.get(f"/bills/getTransactions/{reference}")

    def statistics(self) -> Any:
        """Get bill statistics via ``GET /bills/getStatistics``."""
        return self._http.get("/bills/getStatistics")
