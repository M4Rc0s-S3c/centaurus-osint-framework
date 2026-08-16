"""Tests for deterministic Sublist3r normalization."""

from copy import deepcopy

from centaurus.normalization.sublist3r_normalizer import normalize_sublist3r_data


def test_sublist3r_normalizer_returns_stable_vocabulary() -> None:
    result = normalize_sublist3r_data({})

    assert result == {
        "domain_name": None,
        "subdomains": [],
    }


def test_sublist3r_normalizer_canonicalizes_domain_and_hostnames() -> None:
    result = normalize_sublist3r_data({
        "domain": " Example.COM. ",
        "subdomains": [" WWW.EXAMPLE.COM. ", "Api.Example.Com"],
    })

    assert result["domain_name"] == "example.com"
    assert result["subdomains"] == ["api.example.com", "www.example.com"]


def test_sublist3r_normalizer_deduplicates_equivalent_hostnames() -> None:
    result = normalize_sublist3r_data({
        "domain": "example.com",
        "subdomains": [
            "WWW.EXAMPLE.COM",
            "www.example.com.",
            "www.example.com",
        ],
    })

    assert result["subdomains"] == ["www.example.com"]


def test_sublist3r_normalizer_ignores_non_textual_values() -> None:
    result = normalize_sublist3r_data({
        "domain": "example.com",
        "subdomains": [None, 42, "", "api.example.com"],
    })

    assert result["subdomains"] == ["api.example.com"]


def test_sublist3r_normalizer_handles_non_list_raw_subdomains() -> None:
    result = normalize_sublist3r_data({
        "domain": "example.com",
        "subdomains": "www.example.com",
    })

    assert result["subdomains"] == []


def test_sublist3r_normalizer_does_not_modify_raw_data() -> None:
    data = {
        "domain": "Example.COM.",
        "subdomains": ["WWW.EXAMPLE.COM.", "api.example.com"],
    }
    original = deepcopy(data)

    normalize_sublist3r_data(data)

    assert data == original
