"""Tests for deterministic theHarvester normalization."""

from centaurus.normalization.theharvester_normalizer import (
    normalize_theharvester_data,
)


def test_normalizer_returns_stable_empty_schema() -> None:
    assert normalize_theharvester_data({}) == {
        "domain_name": None,
        "sources": [],
        "hosts": [],
        "subdomains": [],
        "emails": [],
        "ips": [],
        "urls": [],
        "asns": [],
    }


def test_normalizer_canonicalizes_domain_and_sources() -> None:
    result = normalize_theharvester_data({
        "domain": " Example.COM. ",
        "sources": ["URLSCAN", "rapiddns", "urlscan"],
        "report": {},
    })

    assert result["domain_name"] == "example.com"
    assert result["sources"] == ["rapiddns", "urlscan"]


def test_normalizer_deduplicates_hosts_and_derives_scoped_subdomains() -> None:
    result = normalize_theharvester_data({
        "domain": "example.com",
        "report": {
            "hosts": [
                "WWW.EXAMPLE.COM.",
                "api.example.com",
                "www.example.com",
                "example.com",
                "other.example.net",
            ]
        },
    })

    assert result["hosts"] == [
        "api.example.com",
        "example.com",
        "other.example.net",
        "www.example.com",
    ]
    assert result["subdomains"] == [
        "api.example.com",
        "www.example.com",
    ]


def test_normalizer_strips_host_ip_enrichment_before_deriving_subdomains() -> None:
    result = normalize_theharvester_data({
        "domain": "example.com",
        "report": {
            "hosts": [
                "20mail2.EXAMPLE.COM:162.159.50.12",
                "api.example.com:192.0.2.10,192.0.2.11",
            ]
        },
    })

    assert result["hosts"] == [
        "20mail2.example.com",
        "api.example.com",
    ]
    assert result["subdomains"] == [
        "20mail2.example.com",
        "api.example.com",
    ]


def test_normalizer_canonicalizes_emails_without_inventing_scope() -> None:
    result = normalize_theharvester_data({
        "domain": "example.com",
        "report": {
            "emails": [
                " Security@Example.COM ",
                "security@example.com",
                "contact@other.example",
            ]
        },
    })

    assert result["emails"] == [
        "contact@other.example",
        "security@example.com",
    ]


def test_normalizer_preserves_observed_ips_urls_and_asns() -> None:
    result = normalize_theharvester_data({
        "report": {
            "ips": [" 192.0.2.10 ", "192.0.2.10", "2001:db8::1"],
            "interesting_urls": [
                " https://example.com/Login ",
                "https://example.com/Login",
            ],
            "asns": [64500, "AS64501", "AS64501"],
        }
    })

    assert result["ips"] == ["192.0.2.10", "2001:db8::1"]
    assert result["urls"] == ["https://example.com/Login"]
    assert result["asns"] == ["64500", "AS64501"]


def test_normalizer_ignores_invalid_collection_shapes() -> None:
    result = normalize_theharvester_data({
        "domain": 123,
        "sources": "urlscan",
        "report": {
            "hosts": "www.example.com",
            "emails": None,
            "ips": {"ip": "192.0.2.1"},
            "interesting_urls": 42,
            "asns": "AS64500",
        },
    })

    assert result == {
        "domain_name": None,
        "sources": [],
        "hosts": [],
        "subdomains": [],
        "emails": [],
        "ips": [],
        "urls": [],
        "asns": [],
    }


def test_normalizer_does_not_modify_input() -> None:
    report = {
        "hosts": ["WWW.EXAMPLE.COM"],
        "emails": ["Security@Example.COM"],
    }
    data = {
        "domain": "EXAMPLE.COM",
        "sources": ["duckduckgo"],
        "report": report,
    }

    normalize_theharvester_data(data)

    assert data == {
        "domain": "EXAMPLE.COM",
        "sources": ["duckduckgo"],
        "report": {
            "hosts": ["WWW.EXAMPLE.COM"],
            "emails": ["Security@Example.COM"],
        },
    }
