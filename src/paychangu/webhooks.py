"""Webhook signature verification helpers."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any, Union


def verify_signature(
    payload: Union[bytes, str],
    signature: str,
    secret: str,
) -> bool:
    """
    Verify that a standard payment webhook was signed by PayChangu.

    PayChangu sends an HMAC-SHA256 hex digest of the raw request body in the
    ``Signature`` header, keyed with your webhook secret from the dashboard.
    """
    if not signature or not secret:
        return False

    if isinstance(payload, str):
        payload_bytes = payload.encode("utf-8")
    else:
        payload_bytes = payload

    computed = hmac.new(
        secret.encode("utf-8"),
        payload_bytes,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(computed, signature)


def verify_virtual_account_signature(
    data: Any,
    signature: str,
    secret: str,
) -> bool:
    """
    Verify a US virtual-account webhook signature.

    Per PayChangu docs, hash ``json.dumps(data)`` (the webhook ``data`` object)
    with HMAC-SHA256 using your business secret key, then compare to ``signature``.
    """
    if not signature or not secret:
        return False

    if isinstance(data, (bytes, bytearray)):
        payload_bytes = bytes(data)
    elif isinstance(data, str):
        payload_bytes = data.encode("utf-8")
    else:
        # Compact JSON matches the typical server-side encoding used for HMAC.
        payload_bytes = json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

    computed = hmac.new(
        secret.encode("utf-8"),
        payload_bytes,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(computed, signature)
