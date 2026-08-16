"""Tests for deterministic RDAP normalization."""

from centaurus.normalization.rdap_normalizer import normalize_rdap_data


def test_rdap_normalizer_maps_domain_registration_fields() -> None:
    raw = {
        "objectClassName": "domain",
        "handle": "EXAMPLE-1",
        "ldhName": "example.com",
        "status": ["active"],
        "events": [
            {"eventAction": "registration", "eventDate": "1995-08-14T04:00:00Z"},
            {"eventAction": "last changed", "eventDate": "2025-01-01T00:00:00Z"},
            {"eventAction": "expiration", "eventDate": "2030-08-14T04:00:00Z"},
        ],
        "nameservers": [
            {"objectClassName": "nameserver", "ldhName": "ns1.example.com"},
            {"objectClassName": "nameserver", "ldhName": "ns2.example.com"},
        ],
        "secureDNS": {"delegationSigned": True},
        "entities": [
            {
                "objectClassName": "entity",
                "roles": ["registrar"],
                "vcardArray": ["vcard", [["fn", {}, "text", "Example Registrar"]]],
            },
            {
                "objectClassName": "entity",
                "roles": ["registrant"],
                "vcardArray": ["vcard", [["fn", {}, "text", "Example Registrant"]]],
            },
        ],
    }

    result = normalize_rdap_data(raw)

    assert result == {
        "domain_name": "example.com",
        "handle": "EXAMPLE-1",
        "status": ["active"],
        "registrar": "Example Registrar",
        "registrant_name": "Example Registrant",
        "creation_date": "1995-08-14T04:00:00Z",
        "expiration_date": "2030-08-14T04:00:00Z",
        "updated_date": "2025-01-01T00:00:00Z",
        "name_servers": ["ns1.example.com", "ns2.example.com"],
        "dnssec": "signedDelegation",
        "start_address": None,
        "end_address": None,
        "ip_version": None,
        "name": None,
        "type": None,
        "country": None,
    }


def test_rdap_normalizer_maps_unsigned_dnssec() -> None:
    assert normalize_rdap_data({"secureDNS": {"delegationSigned": False}})["dnssec"] == "unsigned"


def test_rdap_normalizer_maps_ip_network_fields() -> None:
    result = normalize_rdap_data({
        "objectClassName": "ip network",
        "handle": "NET-192-0-2-0-1",
        "startAddress": "192.0.2.0",
        "endAddress": "192.0.2.255",
        "ipVersion": "v4",
        "name": "TEST-NET-1",
        "type": "ALLOCATED PA",
        "country": "US",
        "events": [
            {"eventAction": "registration", "eventDate": "2010-01-01T00:00:00Z"},
        ],
    })

    assert result["start_address"] == "192.0.2.0"
    assert result["end_address"] == "192.0.2.255"
    assert result["ip_version"] == "v4"
    assert result["name"] == "TEST-NET-1"
    assert result["type"] == "ALLOCATED PA"
    assert result["country"] == "US"
    assert result["creation_date"] == "2010-01-01T00:00:00Z"


def test_rdap_normalizer_uses_entity_handle_when_vcard_name_is_absent() -> None:
    result = normalize_rdap_data({
        "entities": [
            {"roles": ["registrar"], "handle": "REG-123"},
        ]
    })

    assert result["registrar"] == "REG-123"


def test_rdap_normalizer_preserves_empty_raw_observation() -> None:
    assert normalize_rdap_data({}) == {}


def test_rdap_normalizer_does_not_modify_raw_data() -> None:
    raw = {
        "status": ("active", "locked"),
        "nameservers": [{"ldhName": "ns1.example.com"}],
    }

    normalize_rdap_data(raw)

    assert raw["status"] == ("active", "locked")
    assert raw["nameservers"] == [{"ldhName": "ns1.example.com"}]
