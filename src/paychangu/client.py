"""PayChangu API client."""

from __future__ import annotations

from typing import Any, Optional, Union

from ._http import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, HttpClient
from .models.payment import Payment
from .models.payout import MobileMoneyPayout
from .resources.bills import BillsResource
from .resources.cards import CardsResource
from .resources.connect import ConnectResource
from .resources.direct_charge import DirectChargeResource
from .resources.payments import PaymentsResource
from .resources.payouts import PayoutsResource
from .resources.virtual_accounts import VirtualAccountsResource
from .resources.wallet import WalletResource


class PayChanguClient:
    """
    High-level client for the PayChangu API.

    Example::

        from paychangu import PayChanguClient

        client = PayChanguClient(secret_key="SEC-...")
        balance = client.wallet.balance("MWK")

    For PayChangu Connect, build a client with the merchant's access token::

        connected = PayChanguClient.from_access_token("access-token-from-redirect")
        connected.payments.initiate(...)
    """

    def __init__(
        self,
        secret_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.secret_key = secret_key
        self.base_url = base_url
        self.timeout = timeout
        self._http = HttpClient(secret_key, base_url=base_url, timeout=timeout)
        self.payments = PaymentsResource(self._http)
        self.direct_charge = DirectChargeResource(self._http)
        self.payouts = PayoutsResource(self._http)
        self.bills = BillsResource(self._http)
        self.cards = CardsResource(self._http)
        self.wallet = WalletResource(self._http)
        self.connect = ConnectResource(self._http)
        self.virtual_accounts = VirtualAccountsResource(self._http)

        # Backwards-compatible service aliases from earlier SDK versions.
        self.payout_service = _LegacyPayoutService(self)
        self.airtime_service = _LegacyAirtimeService(self)
        self.direct_charge_service = _LegacyDirectChargeService(self)

    @classmethod
    def from_access_token(
        cls,
        access_token: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> "PayChanguClient":
        """
        Create a client that authenticates with a Connect access token.

        Use this after a merchant authorizes your app and is redirected back
        with an access token.
        """
        if not access_token:
            raise ValueError("access_token is required")
        return cls(secret_key=access_token, base_url=base_url, timeout=timeout)

    def initiate_transaction(self, payment: Union[Payment, dict[str, Any]]) -> Any:
        """Alias for ``client.payments.initiate``."""
        return self.payments.initiate(payment)

    def verify_transaction(self, tx_ref: str) -> Any:
        """Alias for ``client.payments.verify``."""
        return self.payments.verify(tx_ref)

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._http.close()

    def __enter__(self) -> "PayChanguClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class _LegacyPayoutService:
    """Compatibility wrapper matching the previous nested payout service API."""

    def __init__(self, client: PayChanguClient) -> None:
        self._client = client

    def get_operators(self) -> Any:
        return self._client.payouts.momo_operators()

    def initiate_payout(self, payout: Union[MobileMoneyPayout, dict[str, Any]]) -> Any:
        return self._client.payouts.initiate_momo(payout)

    def fetch_transfer(self, charge_id: str) -> Any:
        return self._client.payouts.momo_details(charge_id)


class _LegacyAirtimeService:
    """Compatibility wrapper; prefer ``client.bills.buy_airtime``."""

    def __init__(self, client: PayChanguClient) -> None:
        self._client = client

    def buy_airtime(
        self,
        phone: str,
        amount: Union[int, float, str],
        reference: Optional[str] = None,
    ) -> Any:
        return self._client.bills.buy_airtime(phone=phone, amount=amount, reference=reference)


class _LegacyDirectChargeService:
    """Compatibility wrapper matching the previous nested direct-charge service API."""

    def __init__(self, client: PayChanguClient) -> None:
        self._client = client

    def get_supported_operators(self) -> Any:
        return self._client.direct_charge.operators()

    def initialize_payment(
        self,
        mobile: str,
        mobile_money_operator_ref_id: str,
        amount: Union[int, float, str],
        charge_id: str,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> Any:
        return self._client.direct_charge.initialize(
            mobile=mobile,
            mobile_money_operator_ref_id=mobile_money_operator_ref_id,
            amount=amount,
            charge_id=charge_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

    def verify_charge(self, charge_id: str) -> Any:
        return self._client.direct_charge.verify(charge_id)

    def get_charge_details(self, charge_id: str) -> Any:
        return self._client.direct_charge.details(charge_id)
