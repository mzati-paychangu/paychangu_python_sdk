"""US virtual bank account resources."""

from __future__ import annotations

from typing import Any, Optional, Union

from .._http import HttpClient
from .._utils import model_to_dict, omit_none
from ..models.virtual_account import VirtualCustomer


class VirtualAccountsResource:
    """
    Issue and manage USD virtual bank accounts for customers.

    Flow: create customer → complete KYC (webhook) → create US account.
    """

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def create_customer(
        self,
        customer: Optional[Union[VirtualCustomer, dict[str, Any]]] = None,
        *,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> Any:
        """Create a customer via ``POST /virtual-account/api/customers/create``."""
        if customer is not None:
            payload = model_to_dict(customer) if not isinstance(customer, dict) else omit_none(customer)
        else:
            if not email or not first_name or not last_name:
                raise ValueError("email, first_name, and last_name are required")
            payload = {
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
            }
        return self._http.post("/virtual-account/api/customers/create", json=payload)

    def list_customers(
        self,
        *,
        page: Optional[Union[int, str]] = None,
        per_page: Optional[Union[int, str]] = None,
    ) -> Any:
        """List customers via ``GET /virtual-account/api/customers``."""
        params = omit_none(
            {
                "page": str(page) if page is not None else None,
                "per_page": str(per_page) if per_page is not None else None,
            }
        )
        return self._http.get("/virtual-account/api/customers", params=params or None)

    def get_customer(self, customer_id: str) -> Any:
        """Get a customer via ``GET /virtual-account/api/customers/{customerId}``."""
        return self._http.get(f"/virtual-account/api/customers/{customer_id}")

    def update_customer(
        self,
        customer_id: str,
        customer: Optional[Union[VirtualCustomer, dict[str, Any]]] = None,
        *,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> Any:
        """Update a customer via ``PUT /virtual-account/api/customers/{customerId}``."""
        if customer is not None:
            payload = model_to_dict(customer) if not isinstance(customer, dict) else omit_none(customer)
        else:
            payload = omit_none(
                {
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                }
            )
            if not payload:
                raise ValueError("Provide at least one of email, first_name, last_name")
        return self._http.put(f"/virtual-account/api/customers/{customer_id}", json=payload)

    def delete_customer(self, customer_id: str) -> Any:
        """Delete a customer via ``DELETE /virtual-account/api/customers/{customerId}``."""
        return self._http.delete(f"/virtual-account/api/customers/{customer_id}")

    def create_account(self, customer_id: str) -> Any:
        """
        Create a US virtual account for a KYC-approved customer.

        Documented as ``GET /virtual-account/api/customers/{customerId}/virtual-account``.
        """
        return self._http.get(f"/virtual-account/api/customers/{customer_id}/virtual-account")

    def deactivate_account(self, customer_id: str) -> Any:
        """Deactivate a US account via ``.../virtual-account/deactivate``."""
        return self._http.get(
            f"/virtual-account/api/customers/{customer_id}/virtual-account/deactivate"
        )

    def reactivate_account(self, customer_id: str) -> Any:
        """Reactivate a US account via ``POST .../virtual-account/reactivate``."""
        return self._http.post(
            f"/virtual-account/api/customers/{customer_id}/virtual-account/reactivate"
        )

    def account_activity(self, customer_id: str) -> Any:
        """List US account activity via ``GET .../virtual-account/activities``."""
        return self._http.get(
            f"/virtual-account/api/customers/{customer_id}/virtual-account/activities"
        )
