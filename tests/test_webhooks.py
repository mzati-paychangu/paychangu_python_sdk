"""Tests for webhook signature verification."""

import hashlib
import hmac

from paychangu.webhooks import verify_signature


def test_verify_signature_accepts_valid_hmac():
    secret = "whsec_test"
    payload = b'{"status":"success","amount":1000}'
    signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    assert verify_signature(payload, signature, secret) is True
    assert verify_signature(payload.decode(), signature, secret) is True


def test_verify_signature_rejects_invalid_hmac():
    assert verify_signature(b"{}", "deadbeef", "secret") is False
    assert verify_signature(b"{}", "", "secret") is False
    assert verify_signature(b"{}", "abc", "") is False
