"""Template for a narrow, deterministic tool."""

from __future__ import annotations


def run(value: str) -> str:
    """Return a transformed value.

    Replace this function with the tool's real public interface. Keep the
    signature explicit and document any side effects.
    """
    if not isinstance(value, str):
        raise TypeError("value must be a string")
    return value
