"""Tests for deterministic crt.sh normalization."""

from copy import deepcopy

from centaurus.normalization.crtsh_normalizer import normalize_crtsh_data


def _row(**overrides):
    row = {
        "issuer_ca_id": 123,
        "issuer_name": "C=US, O=Example CA, CN=Example Issuer",
        "common_name": "WWW.EXAMPLE.COM",
        "name_value": "WWW.EXAMPLE.COM\napi.example.com\n*.dev.example.com",
        "id": 456,
        "entry_timestamp": "2026-08-16T10:00:00.000",
        "not_before": "2026-08-16T09:00:00",
        "not_after": "2026-11-14T09:00:00",
        "serial_number": "01AB",
    }
    row.update(overrides)
    return row


def test_crtsh_normalizer_materializes_stable_vocabulary() -> None:
    result = normalize_crtsh_data({
        "domain": "Example.COM.",
        "certificates": [_row()],
    })

    assert result["domain_name"] == "example.com"
    assert result["certificate_names"] == [
        "*.dev.example.com",
        "api.example.com",
        "www.example.com",
    ]
    assert result["subdomains"] == [
        "api.example.com",
        "dev.example.com",
        "www.example.com",
    ]


def test_crtsh_normalizer_maps_certificate_fields() -> None:
    result = normalize_crtsh_data({
        "domain": "example.com",
        "certificates": [_row()],
    })

    certificate = result["certificates"][0]
    assert certificate == {
        "issuer_ca_id": 123,
        "issuer_name": "C=US, O=Example CA, CN=Example Issuer",
        "common_name": "www.example.com",
        "names": [
            "*.dev.example.com",
            "api.example.com",
            "www.example.com",
        ],
        "certificate_id": 456,
        "entry_timestamp": "2026-08-16T10:00:00.000",
        "not_before": "2026-08-16T09:00:00",
        "not_after": "2026-11-14T09:00:00",
        "serial_number": "01AB",
    }


def test_crtsh_normalizer_accepts_legacy_minimum_identifiers() -> None:
    result = normalize_crtsh_data({
        "domain": "example.com",
        "certificates": [
            _row(
                id=None,
                entry_timestamp=None,
                min_cert_id=789,
                min_entry_timestamp="2026-08-15T08:00:00",
            )
        ],
    })

    certificate = result["certificates"][0]
    assert certificate["certificate_id"] == 789
    assert certificate["entry_timestamp"] == "2026-08-15T08:00:00"


def test_crtsh_normalizer_deduplicates_names_across_certificates() -> None:
    result = normalize_crtsh_data({
        "domain": "example.com",
        "certificates": [
            _row(name_value="www.example.com\napi.example.com"),
            _row(common_name="api.example.com", name_value="WWW.EXAMPLE.COM."),
        ],
    })

    assert result["certificate_names"] == [
        "api.example.com",
        "www.example.com",
    ]
    assert result["subdomains"] == [
        "api.example.com",
        "www.example.com",
    ]


def test_crtsh_normalizer_excludes_names_outside_requested_domain() -> None:
    result = normalize_crtsh_data({
        "domain": "example.com",
        "certificates": [
            _row(
                common_name="other.test",
                name_value="api.example.com\nother.test\n*.outside.test",
            )
        ],
    })

    assert result["certificate_names"] == [
        "*.outside.test",
        "api.example.com",
        "other.test",
    ]
    assert result["subdomains"] == ["api.example.com"]


def test_crtsh_normalizer_handles_empty_or_invalid_certificate_collection() -> None:
    assert normalize_crtsh_data({}) == {
        "domain_name": None,
        "certificates": [],
        "certificate_names": [],
        "subdomains": [],
    }
    assert normalize_crtsh_data({"domain": "example.com", "certificates": "bad"}) == {
        "domain_name": "example.com",
        "certificates": [],
        "certificate_names": [],
        "subdomains": [],
    }


def test_crtsh_normalizer_does_not_modify_raw_input() -> None:
    raw = {
        "domain": "Example.COM.",
        "certificates": [_row()],
    }
    original = deepcopy(raw)

    normalize_crtsh_data(raw)

    assert raw == original
