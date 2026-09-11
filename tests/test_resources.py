"""Integration-style unit tests for API resources using mocked HTTP."""

import json

import responses

from paychangu import (
    AirtimePurchase,
    BankPayout,
    MobileMoneyCharge,
    MobileMoneyPayout,
    PayChanguClient,
    Payment,
)


BASE = "https://api.paychangu.com"


@responses.activate
def test_initiate_and_verify_payment():
    responses.add(
        responses.POST,
        f"{BASE}/payment",
        json={"status": "success", "data": {"checkout_url": "https://checkout.example"}},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/verify-payment/tx-1",
        json={"status": "success", "data": {"status": "success"}},
        status=200,
    )

    client = PayChanguClient(secret_key="SEC-test")
    payment = Payment(
        amount=1000,
        currency="MWK",
        callback_url="https://example.com/callback",
        return_url="https://example.com/return",
        tx_ref="tx-1",
        email=None,
    )
    result = client.initiate_transaction(payment)
    assert result["status"] == "success"
    assert json.loads(responses.calls[0].request.body)["amount"] == "1000"
    assert "email" not in json.loads(responses.calls[0].request.body)

    verified = client.verify_transaction("tx-1")
    assert verified["data"]["status"] == "success"


@responses.activate
def test_direct_charge_initialize_omits_none():
    responses.add(
        responses.POST,
        f"{BASE}/mobile-money/payments/initialize",
        json={"status": "success"},
        status=200,
    )
    client = PayChanguClient(secret_key="SEC-test")
    client.direct_charge.initialize(
        MobileMoneyCharge(
            mobile="265999000111",
            mobile_money_operator_ref_id="op-1",
            amount=50,
            charge_id="c-1",
            email=None,
        )
    )
    body = json.loads(responses.calls[0].request.body)
    assert body == {
        "mobile": "265999000111",
        "mobile_money_operator_ref_id": "op-1",
        "amount": "50",
        "charge_id": "c-1",
    }


@responses.activate
def test_momo_payout_payload_fields():
    responses.add(
        responses.POST,
        f"{BASE}/mobile-money/payouts/initialize",
        json={"status": "success"},
        status=200,
    )
    client = PayChanguClient(secret_key="SEC-test")
    client.payouts.initiate_momo(
        MobileMoneyPayout(
            mobile="265999000111",
            mobile_money_operator_ref_id="op-1",
            amount=100,
            charge_id="p-1",
        )
    )
    body = json.loads(responses.calls[0].request.body)
    assert body["mobile"] == "265999000111"
    assert body["charge_id"] == "p-1"
    assert "mobile_number" not in body


@responses.activate
def test_buy_airtime_endpoint():
    responses.add(
        responses.POST,
        f"{BASE}/bills/buy-airtime",
        json={"status": "success"},
        status=200,
    )
    client = PayChanguClient(secret_key="SEC-test")
    client.bills.buy_airtime(AirtimePurchase(phone="098000099", amount=1000, reference="PC1"))
    assert responses.calls[0].request.url.endswith("/bills/buy-airtime")
    body = json.loads(responses.calls[0].request.body)
    assert body == {"phone": "098000099", "amount": "1000", "reference": "PC1"}


@responses.activate
def test_wallet_balance():
    responses.add(
        responses.GET,
        f"{BASE}/wallet-balance",
        json={
            "status": "success",
            "data": {"currency": "MWK", "main_balance": "1000"},
        },
        status=200,
    )
    client = PayChanguClient(secret_key="SEC-test")
    result = client.wallet.balance("MWK")
    assert result["data"]["currency"] == "MWK"
    assert "currency=MWK" in responses.calls[0].request.url


@responses.activate
def test_bank_payout_and_banks_list():
    responses.add(
        responses.GET,
        f"{BASE}/direct-charge/payouts/supported-banks",
        json={"status": "success", "data": [{"uuid": "bank-1", "name": "NBM"}]},
        status=200,
    )
    responses.add(
        responses.POST,
        f"{BASE}/direct-charge/payouts/initialize",
        json={"status": "success"},
        status=200,
    )
    client = PayChanguClient(secret_key="SEC-test")
    banks = client.payouts.banks("MWK")
    assert banks["data"][0]["uuid"] == "bank-1"

    client.payouts.initiate_bank(
        BankPayout(
            bank_uuid="bank-1",
            amount=3000,
            charge_id="bp-1",
            bank_account_name="Jane Doe",
            bank_account_number="1000000010",
        )
    )
    body = json.loads(responses.calls[1].request.body)
    assert body["payout_method"] == "bank_transfer"
    assert body["amount"] == "3000"


@responses.activate
def test_card_charge_verify_refund():
    responses.add(
        responses.POST,
        f"{BASE}/charge-card/payments",
        json={"success": True},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/charge-card/verify/charge_1",
        json={"status": "success"},
        status=200,
    )
    responses.add(
        responses.POST,
        f"{BASE}/charge-card/refund/charge_1",
        json={"status": "success"},
        status=200,
    )
    client = PayChanguClient(secret_key="SEC-test")
    client.cards.charge(
        card_number="4242424242424242",
        expiry="12/30",
        cvv="123",
        cardholder_name="John Doe",
        amount=1000,
        currency="USD",
        charge_id="charge_1",
        redirect_url="https://example.com/redirect",
    )
    client.cards.verify("charge_1")
    client.cards.refund("charge_1")
    assert len(responses.calls) == 3


@responses.activate
def test_legacy_aliases():
    responses.add(
        responses.GET,
        f"{BASE}/mobile-money",
        json={"status": "success", "data": []},
        status=200,
    )
    responses.add(
        responses.POST,
        f"{BASE}/bills/buy-airtime",
        json={"status": "success"},
        status=200,
    )
    client = PayChanguClient(secret_key="SEC-test")
    client.direct_charge_service.get_supported_operators()
    client.airtime_service.buy_airtime(phone="098000099", amount=500)
    assert len(responses.calls) == 2
