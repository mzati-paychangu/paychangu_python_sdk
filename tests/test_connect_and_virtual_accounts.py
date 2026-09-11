"""Tests for Connect and US virtual accounts."""

import hashlib
import hmac
import json

import pytest
import responses

from paychangu import (
    ConnectAuthorizeParams,
    PayChanguClient,
    VirtualCustomer,
    verify_virtual_account_signature,
)

BASE = "https://api.paychangu.com"


@responses.activate
def test_connect_authorize_link():
    responses.add(
        responses.POST,
        f"{BASE}/connect/authorize-link",
        json={"status": "success", "data": {"url": "https://connect.paychangu.com/xyz"}},
        status=200,
    )
    client = PayChanguClient(secret_key="SEC-test")
    result = client.connect.authorize_link(
        client_id="app_123",
        redirect_uri="https://example.com/callback",
        mode="test",
        scope="payments:write payments:read",
    )
    assert result["data"]["url"].startswith("https://connect.paychangu.com/")
    assert "client_id=app_123" in responses.calls[0].request.url
    assert "mode=test" in responses.calls[0].request.url


@responses.activate
def test_connect_authorize_link_model_and_validation():
    responses.add(
        responses.POST,
        f"{BASE}/connect/authorize-link",
        json={"status": "success"},
        status=200,
    )
    client = PayChanguClient(secret_key="SEC-test")
    client.connect.authorize_link(
        ConnectAuthorizeParams(
            client_id="app_123",
            redirect_uri="https://example.com/callback",
            mode="live",
            wh_url="https://example.com/wh",
        )
    )
    assert "wh_url=" in responses.calls[0].request.url

    with pytest.raises(ValueError, match="mode must be"):
        client.connect.authorize_link(
            client_id="app_123",
            redirect_uri="https://example.com/callback",
            mode="sandbox",
        )


@responses.activate
def test_connect_user_and_revoke():
    responses.add(
        responses.GET,
        f"{BASE}/connect/user",
        json={"status": "success", "data": {"name": "Merchant"}},
        status=200,
    )
    responses.add(
        responses.POST,
        f"{BASE}/connect/revoke",
        json={"status": "success"},
        status=200,
    )
    client = PayChanguClient(secret_key="SEC-test")
    user = client.connect.user(access_token="tok_abc")
    assert user["data"]["name"] == "Merchant"
    assert "access_token=tok_abc" in responses.calls[0].request.url

    client.connect.revoke("tok_abc")
    assert "token=tok_abc" in responses.calls[1].request.url


def test_from_access_token_sets_bearer():
    connected = PayChanguClient.from_access_token("merchant-access-token")
    assert connected.secret_key == "merchant-access-token"
    assert "merchant-access-token" in connected._http._session.headers["Authorization"]


@responses.activate
def test_virtual_customer_crud_and_account_lifecycle():
    responses.add(
        responses.POST,
        f"{BASE}/virtual-account/api/customers/create",
        json={"status": "success", "data": {"id": "cus_1"}},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/virtual-account/api/customers",
        json={"status": "success", "data": []},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/virtual-account/api/customers/cus_1",
        json={"status": "success", "data": {"id": "cus_1"}},
        status=200,
    )
    responses.add(
        responses.PUT,
        f"{BASE}/virtual-account/api/customers/cus_1",
        json={"status": "success"},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/virtual-account/api/customers/cus_1/virtual-account",
        json={"status": "success", "data": {"account_number": "123"}},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/virtual-account/api/customers/cus_1/virtual-account/deactivate",
        json={"status": "success"},
        status=200,
    )
    responses.add(
        responses.POST,
        f"{BASE}/virtual-account/api/customers/cus_1/virtual-account/reactivate",
        json={"status": "success"},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/virtual-account/api/customers/cus_1/virtual-account/activities",
        json={"status": "success", "data": []},
        status=200,
    )
    responses.add(
        responses.DELETE,
        f"{BASE}/virtual-account/api/customers/cus_1",
        json={"status": "success"},
        status=200,
    )

    client = PayChanguClient(secret_key="SEC-test")
    created = client.virtual_accounts.create_customer(
        VirtualCustomer(email="john@example.com", first_name="John", last_name="Banda")
    )
    assert created["data"]["id"] == "cus_1"
    body = json.loads(responses.calls[0].request.body)
    assert body == {
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Banda",
    }

    client.virtual_accounts.list_customers(page=1, per_page=20)
    client.virtual_accounts.get_customer("cus_1")
    client.virtual_accounts.update_customer("cus_1", first_name="Jon")
    client.virtual_accounts.create_account("cus_1")
    client.virtual_accounts.deactivate_account("cus_1")
    client.virtual_accounts.reactivate_account("cus_1")
    client.virtual_accounts.account_activity("cus_1")
    client.virtual_accounts.delete_customer("cus_1")
    assert len(responses.calls) == 9


def test_verify_virtual_account_signature():
    secret = "SEC-business"
    data = {
        "customer_id": "cus_123456",
        "kyc_status": "approved",
        "rejection_reason": None,
        "timestamp": "2025-06-27T12:34:56Z",
    }
    payload = json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    assert verify_virtual_account_signature(data, signature, secret) is True
    assert verify_virtual_account_signature(data, "bad", secret) is False
