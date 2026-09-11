# PayChangu SDK for Python

Python SDK for the [PayChangu](https://developer.paychangu.com) payment API. Accept hosted checkout, mobile money, bank transfer, and card payments; send MoMo and bank payouts; pay bills and airtime; manage PayChangu Connect and US virtual accounts; and verify webhooks.

Requires **Python 3.9+**.

## Installation

```bash
pip install paychangu
```

From source:

```bash
pip install -e ".[dev]"
```

## Quick start

```python
from paychangu import PayChanguClient, Payment

client = PayChanguClient(secret_key="SEC-your-secret-key")

payment = Payment(
    amount=1000,
    currency="MWK",
    callback_url="https://example.com/callback",
    return_url="https://example.com/return",
    tx_ref="unique-tx-ref",
    first_name="John",
    last_name="Doe",
    email="user@example.com",
    customization={"title": "Order #1", "description": "Checkout"},
)
session = client.payments.initiate(payment)
# session["data"]["checkout_url"]

status = client.payments.verify("unique-tx-ref")
```

Use a context manager to close the HTTP session:

```python
with PayChanguClient(secret_key="SEC-...") as client:
    print(client.wallet.balance("MWK"))
```

## Features

| Area | Client API |
|------|------------|
| Hosted checkout | `client.payments.initiate` / `verify` |
| MoMo direct charge | `client.direct_charge.operators` / `initialize` / `verify` / `details` |
| Bank transfer charge | `client.direct_charge.initialize_bank_transfer` / `bank_transfer_details` |
| MoMo payouts | `client.payouts.momo_operators` / `initiate_momo` / `momo_details` |
| Bank payouts | `client.payouts.banks` / `initiate_bank` / `bank_details` / `list_bank_payouts` |
| Bills & airtime | `client.bills.billers` / `validate` / `pay` / `buy_airtime` / … |
| Cards | `client.cards.charge` / `verify` / `refund` |
| Wallet | `client.wallet.balance` |
| Connect | `client.connect.authorize_link` / `user` / `revoke` |
| US virtual accounts | `client.virtual_accounts.*` |
| Webhooks | `verify_signature` / `verify_virtual_account_signature` |

API reference: [developer.paychangu.com](https://developer.paychangu.com/llms.txt).

## Usage examples

### Direct MoMo charge

```python
from paychangu import MobileMoneyCharge

operators = client.direct_charge.operators()
op_ref = operators["data"][0]["ref_id"]

result = client.direct_charge.initialize(
    MobileMoneyCharge(
        mobile="265999000111",
        mobile_money_operator_ref_id=op_ref,
        amount=500,
        charge_id="charge-unique-1",
        first_name="John",
    )
)
client.direct_charge.verify("charge-unique-1")
```

### MoMo payout

```python
from paychangu import MobileMoneyPayout

client.payouts.initiate_momo(
    MobileMoneyPayout(
        mobile="265999000111",
        mobile_money_operator_ref_id=op_ref,
        amount=1000,
        charge_id="payout-unique-1",
    )
)
```

### Bank payout

```python
from paychangu import BankPayout

banks = client.payouts.banks(currency="MWK")
bank_uuid = banks["data"][0]["uuid"]

client.payouts.initiate_bank(
    BankPayout(
        bank_uuid=bank_uuid,
        amount=3000,
        charge_id="bank-payout-1",
        bank_account_name="Jane Doe",
        bank_account_number="1000000010",
    )
)
```

### Bills and airtime

```python
from paychangu import AirtimePurchase, BillPayment

client.bills.billers()
client.bills.validate(biller="escom", account="917535617", amount=10000)
client.bills.pay(
    BillPayment(
        biller="escom",
        account="917535617",
        amount=10000,
        customer_name="John Phiri",
        reference="FY826245",
    )
)
client.bills.buy_airtime(AirtimePurchase(phone="098000099", amount=1000, reference="PC62537"))
```

### PayChangu Connect

```python
link = client.connect.authorize_link(
    client_id="your_app_client_id",
    redirect_uri="https://example.com/connect/callback",
    mode="test",  # or "live"
    scope="payments:write payments:read",
    wh_url="https://example.com/webhooks/connect",
)
# Redirect the merchant to link["data"]["url"] (response shape may vary)

# After redirect, use the access token for that merchant:
connected = PayChanguClient.from_access_token("access-token-from-redirect")
connected.payments.initiate(...)

client.connect.user(access_token="access-token-from-redirect")
client.connect.revoke("access-token-from-redirect")
```

### US virtual accounts

```python
from paychangu import VirtualCustomer, verify_virtual_account_signature

customer = client.virtual_accounts.create_customer(
    VirtualCustomer(email="john@example.com", first_name="John", last_name="Banda")
)
# Redirect user through KYC; wait for kyc_updated webhook, then:
client.virtual_accounts.create_account(customer_id="cus_123")
client.virtual_accounts.account_activity("cus_123")
client.virtual_accounts.deactivate_account("cus_123")
client.virtual_accounts.reactivate_account("cus_123")

# Virtual-account webhooks sign the `data` object:
ok = verify_virtual_account_signature(
    data=webhook_json["data"],
    signature=webhook_json["signature"],
    secret="your_business_secret_key",
)
```

### Card charge (PCI)

Only call card APIs from a **PCI-compliant** environment. Prefer hosted checkout when you do not need to handle PAN/CVV yourself.

```python
from paychangu import CardCharge

client.cards.charge(
    CardCharge(
        card_number="4242424242424242",
        expiry="12/30",
        cvv="123",
        cardholder_name="John Doe",
        amount=1000,
        currency="USD",
        charge_id="charge_12345",
        redirect_url="https://example.com/redirect",
        email="user@example.com",
    )
)
client.cards.verify("charge_12345")
```

### Webhook verification

```python
from paychangu import verify_signature

ok = verify_signature(
    payload=request_body,  # raw bytes or str
    signature=request_headers["Signature"],
    secret="your_webhook_secret",
)
if not ok:
    # reject the request
    ...
```

### Errors

```python
from paychangu import APIError, AuthenticationError, ValidationError

try:
    client.wallet.balance()
except ValidationError as exc:
    print(exc.status_code, exc.message, exc.body)
except AuthenticationError as exc:
    print("Check your secret key", exc)
except APIError as exc:
    print(exc)
```

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Breaking changes in 0.2.0 / 0.1.0

### 0.2.0
- Added Connect and US virtual accounts; version bump only for new surface area.

### 0.1.0
- MoMo payouts now use `mobile`, `mobile_money_operator_ref_id`, and `charge_id` (aligned with the live API).
- Airtime uses `POST /bills/buy-airtime` via `client.bills.buy_airtime` (old `/bill_payment/*` paths removed).
- Resource access is via `client.payments`, `client.direct_charge`, `client.payouts`, `client.bills`, `client.cards`, and `client.wallet`. Legacy aliases (`initiate_transaction`, `direct_charge_service`, …) remain where practical.
- Python 3.9+ is required.

## Support

- Docs: [developer.paychangu.com](https://developer.paychangu.com)
- Email: support@paychangu.com
