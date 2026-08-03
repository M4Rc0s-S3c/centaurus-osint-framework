"""
Deterministic normalization of WHOIS RAW data.
"""

from datetime import date, datetime
from typing import Any


def normalize_whois_data(
    data: dict[str, Any],
) -> dict[str, Any]:
    """
    Normalize WHOIS RAW data without interpreting its meaning.

    The normalizer only stabilizes data representation:

    - datetime/date values become ISO-8601 strings;
    - lists and tuples are normalized recursively;
    - dictionaries are normalized recursively;
    - None values are preserved;
    - scalar values are preserved.

    No semantic interpretation is performed.
    """

    return _normalize_value(data)


def _normalize_value(
    value: Any,
) -> Any:
    """
    Normalize one arbitrary WHOIS value recursively.
    """

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            key: _normalize_value(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            _normalize_value(item)
            for item in value
        ]

    return value