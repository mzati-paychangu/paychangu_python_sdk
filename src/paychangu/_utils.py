"""Shared helpers for request models."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Mapping


def omit_none(data: Mapping[str, Any]) -> dict[str, Any]:
    """Return a shallow copy of ``data`` without ``None`` values."""
    return {key: value for key, value in data.items() if value is not None}


def dataclass_payload(model: Any) -> dict[str, Any]:
    """Serialize a dataclass instance, omitting ``None`` values."""
    if not (is_dataclass(model) and not isinstance(model, type)):
        raise TypeError(f"Expected a dataclass instance, got {type(model)!r}")
    return omit_none(asdict(model))


def model_to_dict(model: Any) -> dict[str, Any]:
    """Convert a model into a JSON-ready dict, omitting ``None``."""
    if hasattr(model, "to_dict") and callable(model.to_dict):
        return omit_none(model.to_dict())
    if is_dataclass(model) and not isinstance(model, type):
        return dataclass_payload(model)
    if isinstance(model, Mapping):
        return omit_none(dict(model))
    raise TypeError(f"Unsupported model type: {type(model)!r}")


def stringify_amount(amount: Any) -> str:
    """Normalize amounts to the string form expected by many PayChangu endpoints."""
    if isinstance(amount, bool):
        raise TypeError("amount must be a number or numeric string")
    if isinstance(amount, (int, float)):
        if isinstance(amount, float) and amount.is_integer():
            return str(int(amount))
        return str(amount)
    return str(amount)
