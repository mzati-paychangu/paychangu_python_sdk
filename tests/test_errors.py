"""Tests for HTTP error handling."""

import pytest
import responses

from paychangu import APIError, AuthenticationError, PayChanguClient, ValidationError
from paychangu.exceptions import format_api_message


@responses.activate
def test_validation_error_includes_field_messages():
    responses.add(
        responses.POST,
        "https://api.paychangu.com/payment",
        json={
            "status": "failed",
            "message": {"callback_url": ["The callback url field is required."]},
            "data": None,
        },
        status=400,
    )
    client = PayChanguClient(secret_key="SEC-test")
    with pytest.raises(ValidationError) as exc_info:
        client.payments.initiate(
            {
                "amount": "100",
                "currency": "MWK",
                "callback_url": "https://example.com/cb",
                "return_url": "https://example.com/ret",
            }
        )
    assert exc_info.value.status_code == 400
    assert "callback_url" in str(exc_info.value)


@responses.activate
def test_authentication_error():
    responses.add(
        responses.GET,
        "https://api.paychangu.com/wallet-balance",
        json={"status": "failed", "message": "Unauthorized"},
        status=401,
    )
    client = PayChanguClient(secret_key="SEC-bad")
    with pytest.raises(AuthenticationError):
        client.wallet.balance()


@responses.activate
def test_generic_api_error():
    responses.add(
        responses.GET,
        "https://api.paychangu.com/wallet-balance",
        json={"status": "failed", "message": "Server error"},
        status=500,
    )
    client = PayChanguClient(secret_key="SEC-test")
    with pytest.raises(APIError) as exc_info:
        client.wallet.balance()
    assert exc_info.value.status_code == 500


def test_format_api_message_variants():
    assert format_api_message({"message": "currency is required"}) == "currency is required"
    assert "email" in format_api_message({"message": {"email": ["required"]}})
    assert format_api_message(None) == "Unknown API error"


def test_missing_secret_key_raises():
    with pytest.raises(ValueError):
        PayChanguClient(secret_key="")
