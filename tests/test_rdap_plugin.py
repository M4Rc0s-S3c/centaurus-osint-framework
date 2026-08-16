"""Unit tests for the RDAP plugin."""

from datetime import datetime, timezone

import httpx
import pytest

from centaurus.evidence import EvidenceSource, RawObservation
from centaurus.plugins.rdap.plugin import Plugin


class FakeResponse:
    def __init__(self, data: dict) -> None:
        self._data = data

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._data


def test_rdap_plugin_can_be_created() -> None:
    assert Plugin() is not None


def test_rdap_domain_lookup_uses_iana_bootstrap(monkeypatch) -> None:
    calls: list[str] = []

    def fake_get(url: str, **kwargs) -> FakeResponse:
        calls.append(url)
        if url == "https://data.iana.org/rdap/dns.json":
            return FakeResponse({
                "services": [
                    [["com"], ["https://rdap.example/registry/"]],
                ]
            })
        assert url == "https://rdap.example/registry/domain/example.com"
        return FakeResponse({"objectClassName": "domain", "ldhName": "example.com"})

    monkeypatch.setattr(httpx, "get", fake_get)

    result = Plugin().execute({"domain": "example.com"})

    assert isinstance(result, RawObservation)
    assert result.source is EvidenceSource.RDAP
    assert result.data["ldhName"] == "example.com"
    assert calls == [
        "https://data.iana.org/rdap/dns.json",
        "https://rdap.example/registry/domain/example.com",
    ]
    assert isinstance(result.collected_at, datetime)
    assert result.collected_at.tzinfo == timezone.utc


def test_rdap_ipv4_lookup_uses_most_specific_bootstrap_network(monkeypatch) -> None:
    calls: list[str] = []

    def fake_get(url: str, **kwargs) -> FakeResponse:
        calls.append(url)
        if url == "https://data.iana.org/rdap/ipv4.json":
            return FakeResponse({
                "services": [
                    [["192.0.0.0/8"], ["https://rdap.example/broad/"]],
                    [["192.0.2.0/24"], ["https://rdap.example/specific/"]],
                ]
            })
        assert url == "https://rdap.example/specific/ip/192.0.2.10"
        return FakeResponse({
            "objectClassName": "ip network",
            "startAddress": "192.0.2.0",
            "endAddress": "192.0.2.255",
        })

    monkeypatch.setattr(httpx, "get", fake_get)

    result = Plugin().execute({"ip": "192.0.2.10"})

    assert result.source is EvidenceSource.RDAP
    assert result.data["startAddress"] == "192.0.2.0"
    assert calls[-1] == "https://rdap.example/specific/ip/192.0.2.10"


def test_rdap_ipv6_lookup_uses_ipv6_bootstrap(monkeypatch) -> None:
    calls: list[str] = []

    def fake_get(url: str, **kwargs) -> FakeResponse:
        calls.append(url)
        if url == "https://data.iana.org/rdap/ipv6.json":
            return FakeResponse({
                "services": [
                    [["2001:db8::/32"], ["https://rdap.example/v6/"]],
                ]
            })
        assert url == "https://rdap.example/v6/ip/2001:db8::1"
        return FakeResponse({"objectClassName": "ip network", "ipVersion": "v6"})

    monkeypatch.setattr(httpx, "get", fake_get)

    result = Plugin().execute({"ip": "2001:db8::1"})

    assert result.data["ipVersion"] == "v6"
    assert calls[0] == "https://data.iana.org/rdap/ipv6.json"


def test_rdap_plugin_returns_empty_observation_without_target(monkeypatch) -> None:
    def fail_get(*args, **kwargs):
        raise AssertionError("network must not be used")

    monkeypatch.setattr(httpx, "get", fail_get)

    result = Plugin().execute({})

    assert result.source is EvidenceSource.RDAP
    assert result.data == {}


def test_rdap_plugin_rejects_ambiguous_parameters() -> None:
    with pytest.raises(ValueError, match="either 'domain' or 'ip'"):
        Plugin().execute({"domain": "example.com", "ip": "192.0.2.1"})


def test_rdap_plugin_rejects_unregistered_domain_tld(monkeypatch) -> None:
    monkeypatch.setattr(
        httpx,
        "get",
        lambda *args, **kwargs: FakeResponse({"services": []}),
    )

    with pytest.raises(ValueError, match="No RDAP service registered"):
        Plugin().execute({"domain": "example.invalid"})
