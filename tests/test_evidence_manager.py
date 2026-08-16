"""
Tests for the EvidenceManager domain service.
"""

from datetime import datetime, timezone

import pytest

from centaurus.evidence.evidence import Evidence
from centaurus.evidence.evidence_manager import EvidenceManager
from centaurus.evidence.evidence_source import EvidenceSource
from centaurus.evidence.raw_observation import RawObservation


def _raw_observation(data: dict) -> RawObservation:
    return RawObservation(
        source=EvidenceSource.WHOIS,
        data=data,
        collected_at=datetime(
            2026,
            8,
            12,
            10,
            0,
            tzinfo=timezone.utc,
        ),
    )


def test_create_evidence_returns_evidence() -> None:
    """
    A valid RawObservation produces an Evidence object.
    """

    evidence = EvidenceManager().create_evidence(
        _raw_observation({"domain_name": "EXAMPLE.COM"})
    )

    assert isinstance(evidence, Evidence)


def test_created_evidence_is_immutable() -> None:
    """
    Evidence keeps the frozen domain Value Object contract.
    """

    evidence = EvidenceManager().create_evidence(
        _raw_observation({"domain_name": "EXAMPLE.COM"})
    )

    with pytest.raises((AttributeError, TypeError)):
        evidence.source = EvidenceSource.RDAP  # type: ignore[misc]


def test_evidence_preserves_source() -> None:
    """
    The logical source remains traceable after normalization.
    """

    evidence = EvidenceManager().create_evidence(
        _raw_observation({"domain_name": "EXAMPLE.COM"})
    )

    assert evidence.source is EvidenceSource.WHOIS


def test_evidence_preserves_timestamp() -> None:
    """
    The collection timestamp is preserved unchanged.
    """

    observation = _raw_observation({"domain_name": "EXAMPLE.COM"})

    evidence = EvidenceManager().create_evidence(observation)

    assert evidence.collected_at == observation.collected_at


def test_evidence_contains_normalized_data() -> None:
    """
    WHOIS data is normalized before becoming Evidence.
    """

    collected_at = datetime(
        2026,
        8,
        12,
        10,
        0,
        tzinfo=timezone.utc,
    )
    observation = RawObservation(
        source=EvidenceSource.WHOIS,
        data={
            "domain_name": "EXAMPLE.COM",
            "creation_date": datetime(
                1995,
                8,
                14,
                4,
                0,
                tzinfo=timezone.utc,
            ),
            "name_servers": (
                "NS1.EXAMPLE.COM",
                "NS2.EXAMPLE.COM",
            ),
            "registrant_name": None,
        },
        collected_at=collected_at,
    )

    evidence = EvidenceManager().create_evidence(observation)

    assert evidence.data["domain_name"] == "EXAMPLE.COM"
    assert evidence.data["creation_date"] == "1995-08-14T04:00:00+00:00"
    assert evidence.data["name_servers"] == [
        "NS1.EXAMPLE.COM",
        "NS2.EXAMPLE.COM",
    ]
    assert evidence.data["registrant_name"] is None
    assert evidence.data["registrar"] is None
    assert evidence.data["expiration_date"] is None


def test_normalization_does_not_modify_raw_observation() -> None:
    """
    Normalization leaves the original RAW representation untouched.
    """

    creation_date = datetime(
        1995,
        8,
        14,
        4,
        0,
        tzinfo=timezone.utc,
    )
    raw_data = {
        "creation_date": creation_date,
        "name_servers": (
            "NS1.EXAMPLE.COM",
            "NS2.EXAMPLE.COM",
        ),
    }
    observation = _raw_observation(raw_data)

    EvidenceManager().create_evidence(observation)

    assert observation.data["creation_date"] is creation_date
    assert observation.data["name_servers"] == (
        "NS1.EXAMPLE.COM",
        "NS2.EXAMPLE.COM",
    )


def test_create_evidence_normalizes_rdap_observation() -> None:
    """
    RDAP observations use their tool-specific normalizer before Evidence.
    """

    observation = RawObservation(
        source=EvidenceSource.RDAP,
        data={
            "ldhName": "example.com",
            "events": [
                {
                    "eventAction": "registration",
                    "eventDate": "1995-08-14T04:00:00Z",
                }
            ],
        },
        collected_at=datetime(
            2026,
            8,
            12,
            10,
            0,
            tzinfo=timezone.utc,
        ),
    )

    evidence = EvidenceManager().create_evidence(observation)

    assert evidence.source is EvidenceSource.RDAP
    assert evidence.data["domain_name"] == "example.com"
    assert evidence.data["creation_date"] == "1995-08-14T04:00:00Z"



def test_create_evidence_normalizes_dnsrecon_observation() -> None:
    """DNSRecon observations use their tool-specific normalizer."""

    observation = RawObservation(
        source=EvidenceSource.DNSRECON,
        data={
            "records": [
                {"type": "ScanInfo", "arguments": "dnsrecon", "date": "2026-08-16"},
                {
                    "domain": "example.com",
                    "type": "A",
                    "name": "example.com",
                    "address": "192.0.2.10",
                },
            ]
        },
        collected_at=datetime(2026, 8, 16, 10, 0, tzinfo=timezone.utc),
    )

    evidence = EvidenceManager().create_evidence(observation)

    assert evidence.source is EvidenceSource.DNSRECON
    assert evidence.data["domain_name"] == "example.com"
    assert evidence.data["a_records"] == ["192.0.2.10"]

def test_create_evidence_rejects_invalid_input() -> None:
    """
    EvidenceManager rejects missing or invalid observations.
    """

    manager = EvidenceManager()

    with pytest.raises(ValueError, match="RawObservation cannot be None"):
        manager.create_evidence(None)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="Expected a RawObservation"):
        manager.create_evidence({})  # type: ignore[arg-type]
