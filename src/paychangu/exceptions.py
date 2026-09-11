"""PayChangu SDK exception hierarchy."""

from __future__ import annotations

from typing import Any, Optional


class PayChanguError(Exception):
    """Base exception for all PayChangu SDK errors."""


class NetworkError(PayChanguError):
    """Raised when a network-level failure occurs before a usable HTTP response."""


class APIError(PayChanguError):
    """Raised when the PayChangu API returns an error response."""

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        body: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.body = body

    def __str__(self) -> str:
        if self.status_code is not None:
            return f"HTTP {self.status_code}: {self.message}"
        return self.message


class AuthenticationError(APIError):
    """Raised for 401/403 authentication or authorization failures."""


class ValidationError(APIError):
    """Raised for 400/422 validation failures from the API."""


def format_api_message(body: Any) -> str:
    """Extract a human-readable message from a PayChangu error body."""
    if body is None:
        return "Unknown API error"
    if isinstance(body, str):
        return body
    if not isinstance(body, dict):
        return str(body)

    message = body.get("message")
    if isinstance(message, str) and message:
        return message
    if isinstance(message, dict):
        parts = []
        for field, errors in message.items():
            if isinstance(errors, (list, tuple)):
                parts.append(f"{field}: {', '.join(str(e) for e in errors)}")
            else:
                parts.append(f"{field}: {errors}")
        if parts:
            return "; ".join(parts)

    status = body.get("status")
    if status:
        return f"API request failed with status '{status}'"
    return "API request failed"


def raise_for_api_status(status_code: int, body: Any) -> None:
    """Raise the appropriate typed exception for a non-success status code."""
    message = format_api_message(body)
    if status_code in (401, 403):
        raise AuthenticationError(message, status_code=status_code, body=body)
    if status_code in (400, 422):
        raise ValidationError(message, status_code=status_code, body=body)
    raise APIError(message, status_code=status_code, body=body)
