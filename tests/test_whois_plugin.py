"""
Unit tests for the WHOIS plugin.
"""

from datetime import datetime, timezone

import whois

from centaurus.evidence import EvidenceSource, RawObservation
from centaurus.plugins.whois.plugin import Plugin


def test_whois_plugin_can_be_created() -> None:
    """
    The WHOIS plugin can be instantiated.
    """

    plugin = Plugin()

    assert plugin is not None


def test_whois_plugin_returns_raw_observation(
    monkeypatch,
) -> None:
    """
    The WHOIS plugin returns the raw WHOIS data structure.
    """

    raw_data = {
        "domain_name": "EXAMPLE.COM",
        "registrar": "Example Registrar",
        "creation_date": datetime(
            1995,
            8,
            14,
            4,
            0,
            tzinfo=timezone.utc,
        ),
        "expiration_date": datetime(
            2026,
            8,
            13,
            4,
            0,
            tzinfo=timezone.utc,
        ),
        "name_servers": (
            "NS1.EXAMPLE.COM",
            "NS2.EXAMPLE.COM",
        ),
        "status": [
            "clientTransferProhibited",
        ],
        "registrant_name": None,
    }

    def fake_whois(
        domain: str,
        **kwargs,
    ) -> dict:
        assert domain == "example.com"
        assert kwargs == {
            "timeout": 10,
            "ignore_socket_errors": False,
        }

        return raw_data

    monkeypatch.setattr(
        whois,
        "whois",
        fake_whois,
    )

    plugin = Plugin()

    result = plugin.execute(
        {
            "domain": "example.com",
        }
    )

    assert isinstance(result, RawObservation)
    assert result.source == EvidenceSource.WHOIS
    assert result.data == raw_data
    assert isinstance(result.collected_at, datetime)
    assert result.collected_at.tzinfo == timezone.utc


def test_whois_plugin_passes_domain_to_whois_library(
    monkeypatch,
) -> None:
    """
    The plugin passes the requested domain to python-whois.
    """

    received_domain = None

    def fake_whois(
        domain: str,
        **kwargs,
    ) -> dict:
        nonlocal received_domain

        received_domain = domain
        assert kwargs == {
            "timeout": 10,
            "ignore_socket_errors": False,
        }

        return {
            "domain_name": "EXAMPLE.COM",
        }

    monkeypatch.setattr(
        whois,
        "whois",
        fake_whois,
    )

    plugin = Plugin()

    plugin.execute(
        {
            "domain": "example.com",
        }
    )

    assert received_domain == "example.com"


def test_whois_plugin_handles_unknown_domain_by_default(
) -> None:
    """
    The WHOIS plugin does not execute a lookup when no domain
    is supplied.
    """

    plugin = Plugin()

    result = plugin.execute({})

    assert isinstance(result, RawObservation)
    assert result.source == EvidenceSource.WHOIS
    assert result.data == {}
    assert isinstance(result.collected_at, datetime)
    assert result.collected_at.tzinfo == timezone.utc

def test_whois_plugin_propagates_socket_timeout(monkeypatch) -> None:
    """WHOIS network timeout remains a tool failure, never empty Evidence."""

    def fail_whois(domain: str, **kwargs):
        raise TimeoutError("WHOIS socket timed out")

    monkeypatch.setattr(whois, "whois", fail_whois)

    plugin = Plugin()
    try:
        plugin.execute({"domain": "example.com"})
    except TimeoutError as exc:
        assert str(exc) == "WHOIS socket timed out"
    else:
        raise AssertionError("WHOIS timeout must propagate through the plugin boundary")