"""
Unit tests for deterministic WHOIS normalization.
"""

from datetime import date, datetime, timezone

from centaurus.normalization.whois_normalizer import (
    normalize_whois_data,
)


def test_normalizer_preserves_scalar_values() -> None:
    """
    Scalar values are preserved unchanged.
    """

    data = {
        "domain_name": "EXAMPLE.COM",
        "registrar": "Example Registrar",
        "dnssec": "signedDelegation",
        "missing": None,
    }

    result = normalize_whois_data(data)

    assert result["domain_name"] == "EXAMPLE.COM"
    assert result["registrar"] == "Example Registrar"
    assert result["dnssec"] == "signedDelegation"
    assert result["missing"] is None


def test_normalizer_converts_datetime_to_isoformat() -> None:
    """
    Datetime values are converted to ISO-8601 strings.
    """

    value = datetime(
        1995,
        8,
        14,
        4,
        0,
        0,
        tzinfo=timezone.utc,
    )

    result = normalize_whois_data(
        {
            "creation_date": value,
        }
    )

    assert result["creation_date"] == (
        "1995-08-14T04:00:00+00:00"
    )


def test_normalizer_converts_date_to_isoformat() -> None:
    """
    Date values are converted to ISO-8601 strings.
    """

    value = date(
        2026,
        8,
        13,
    )

    result = normalize_whois_data(
        {
            "expiration_date": value,
        }
    )

    assert result["expiration_date"] == (
        "2026-08-13"
    )


def test_normalizer_converts_tuples_to_lists() -> None:
    """
    Tuple values are normalized into lists.
    """

    result = normalize_whois_data(
        {
            "status": (
                "clientTransferProhibited",
                "clientUpdateProhibited",
            ),
        }
    )

    assert result["status"] == [
        "clientTransferProhibited",
        "clientUpdateProhibited",
    ]


def test_normalizer_normalizes_nested_lists() -> None:
    """
    Nested list values are normalized recursively.
    """

    value = datetime(
        2026,
        1,
        16,
        18,
        26,
        50,
        tzinfo=timezone.utc,
    )

    result = normalize_whois_data(
        {
            "dates": [
                value,
                None,
            ],
        }
    )

    assert result["dates"] == [
        "2026-01-16T18:26:50+00:00",
        None,
    ]


def test_normalizer_normalizes_nested_dictionaries() -> None:
    """
    Nested dictionaries are normalized recursively.
    """

    value = datetime(
        1995,
        8,
        14,
        4,
        0,
        tzinfo=timezone.utc,
    )

    result = normalize_whois_data(
        {
            "registrant": {
                "name": None,
                "organization": "Example Org",
                "created": value,
            },
        }
    )

    assert result["registrant"]["name"] is None
    assert result["registrant"]["organization"] == (
        "Example Org"
    )
    assert result["registrant"]["created"] == (
        "1995-08-14T04:00:00+00:00"
    )


def test_normalizer_preserves_all_input_fields() -> None:
    """
    Normalization does not remove RAW fields.
    """

    data = {
        "domain_name": "EXAMPLE.COM",
        "registrar": "Example Registrar",
        "registrar_url": None,
        "creation_date": date(1995, 8, 14),
        "name_servers": [
            "NS1.EXAMPLE.COM",
            "NS2.EXAMPLE.COM",
        ],
        "status": [
            "clientTransferProhibited",
        ],
    }

    result = normalize_whois_data(data)

    assert set(data.keys()).issubset(result.keys())
    assert result["expiration_date"] is None
    assert result["registrant_name"] is None


def test_normalizer_does_not_modify_input() -> None:
    """
    Normalization does not modify the original RAW structure.
    """

    value = datetime(
        1995,
        8,
        14,
        4,
        0,
        tzinfo=timezone.utc,
    )

    data = {
        "creation_date": value,
        "name_servers": (
            "NS1.EXAMPLE.COM",
            "NS2.EXAMPLE.COM",
        ),
    }

    normalize_whois_data(data)

    assert data["creation_date"] is value
    assert data["name_servers"] == (
        "NS1.EXAMPLE.COM",
        "NS2.EXAMPLE.COM",
    )


def test_normalizer_is_deterministic() -> None:
    """
    The same input produces the same normalized output.
    """

    data = {
        "domain_name": "EXAMPLE.COM",
        "registrar": None,
        "name_servers": [
            "NS1.EXAMPLE.COM",
            "NS2.EXAMPLE.COM",
        ],
        "creation_date": date(1995, 8, 14),
    }

    first = normalize_whois_data(data)
    second = normalize_whois_data(data)

    assert first == second


def test_normalizer_does_not_interpret_none_values() -> None:
    """
    Missing RAW values remain None and are not interpreted.
    """

    result = normalize_whois_data(
        {
            "registrant_name": None,
            "registrant_org": None,
            "country": None,
        }
    )

    assert result["registrant_name"] is None
    assert result["registrant_org"] is None
    assert result["country"] is None

def test_normalizer_materializes_canonical_registration_fields() -> None:
    """Absent registration fields become explicit None values."""

    result = normalize_whois_data({"domain_name": "EXAMPLE.COM"})

    assert result["registrar"] is None
    assert result["name_servers"] is None
    assert result["creation_date"] is None
    assert result["expiration_date"] is None
    assert result["dnssec"] is None
    assert result["registrant_name"] is None
