"""Webhook signature verification helpers."""

from __future__ import annotations

import hashlib
import hmac
from typing import Union


def verify_signature(
    payload: Union[bytes, str],
    signature: str,
    secret: str,
) -> bool:
    """
    Verify that a webhook request was signed by PayChangu.

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
