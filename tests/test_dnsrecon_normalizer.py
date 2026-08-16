"""Tests for deterministic DNSRecon normalization."""

from centaurus.normalization.dnsrecon_normalizer import normalize_dnsrecon_data


def _raw_records() -> dict:
    return {
        "records": [
            {"type": "ScanInfo", "arguments": "dnsrecon -d example.com", "date": "2026-08-16"},
            {"domain": "example.com", "type": "A", "name": "example.com", "address": "192.0.2.10"},
            {"domain": "example.com", "type": "AAAA", "name": "example.com", "address": "2001:db8::10"},
            {"domain": "example.com", "type": "NS", "name": "example.com", "target": "ns1.example.com"},
            {"domain": "example.com", "type": "MX", "name": "example.com", "target": "mail.example.com"},
            {"domain": "example.com", "type": "TXT", "name": "example.com", "text": "v=spf1 -all"},
            {"domain": "example.com", "type": "TXT", "name": "example.com", "text": "verification=abc"},
            {"domain": "example.com", "type": "SRV", "name": "_sip._tcp.example.com", "target": "sip.example.com"},
        ]
    }


def test_dnsrecon_normalizer_returns_stable_dns_vocabulary() -> None:
    result = normalize_dnsrecon_data(_raw_records())

    assert result["domain_name"] == "example.com"
    assert result["a_records"] == ["192.0.2.10"]
    assert result["aaaa_records"] == ["2001:db8::10"]
    assert result["spf_records"] == ["v=spf1 -all"]
    assert len(result["ns_records"]) == 1
    assert len(result["mx_records"]) == 1
    assert len(result["srv_records"]) == 1


def test_dnsrecon_normalizer_separates_scan_info_from_dns_records() -> None:
    result = normalize_dnsrecon_data(_raw_records())

    assert result["scan_info"]["type"] == "ScanInfo"
    assert all(record.get("type") != "ScanInfo" for record in result["records"])


def test_dnsrecon_normalizer_preserves_observed_record_fields() -> None:
    result = normalize_dnsrecon_data(_raw_records())

    assert {record["type"] for record in result["records"]} == {
        "A", "AAAA", "NS", "MX", "TXT", "SRV"
    }


def test_dnsrecon_normalizer_collects_all_txt_records() -> None:
    result = normalize_dnsrecon_data(_raw_records())

    assert result["txt_records"] == ["v=spf1 -all", "verification=abc"]


def test_dnsrecon_normalizer_deduplicates_address_values() -> None:
    data = _raw_records()
    data["records"].append(
        {"domain": "example.com", "type": "A", "name": "example.com", "address": "192.0.2.10"}
    )

    result = normalize_dnsrecon_data(data)

    assert result["a_records"] == ["192.0.2.10"]


def test_dnsrecon_normalizer_handles_missing_records() -> None:
    result = normalize_dnsrecon_data({})

    assert result["domain_name"] is None
    assert result["records"] == []
    assert result["a_records"] == []
    assert result["spf_records"] == []


def test_dnsrecon_normalizer_does_not_modify_raw_data() -> None:
    data = _raw_records()
    original_first = dict(data["records"][0])

    normalize_dnsrecon_data(data)

    assert data["records"][0] == original_first
