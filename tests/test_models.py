"""Tests for request models and helpers."""

from paychangu._utils import omit_none, stringify_amount
from paychangu.models import MobileMoneyPayout, Payment


def test_payment_to_dict_omits_none_and_stringifies_amount():
    payment = Payment(
        amount=1000,
        currency="MWK",
        callback_url="https://example.com/callback",
        return_url="https://example.com/return",
        tx_ref="ref-1",
        email=None,
        first_name="John",
    )
    data = payment.to_dict()
    assert data["amount"] == "1000"
    assert data["currency"] == "MWK"
    assert data["first_name"] == "John"
    assert "email" not in data
    assert "last_name" not in data


def test_momo_payout_uses_api_field_names():
    payout = MobileMoneyPayout(
        mobile="265999000111",
        mobile_money_operator_ref_id="20be6c20-adeb-4b5b-a7ba-0769820df4fb",
        amount=500,
        charge_id="payout-1",
        email=None,
    )
    data = payout.to_dict()
    assert data == {
        "mobile": "265999000111",
        "mobile_money_operator_ref_id": "20be6c20-adeb-4b5b-a7ba-0769820df4fb",
        "amount": "500",
        "charge_id": "payout-1",
    }
    assert "mobile_number" not in data
    assert "network" not in data
    assert "reference" not in data


def test_omit_none_and_stringify_amount():
    assert omit_none({"a": 1, "b": None}) == {"a": 1}
    assert stringify_amount(10) == "10"
    assert stringify_amount(10.5) == "10.5"
    assert stringify_amount("25") == "25"
