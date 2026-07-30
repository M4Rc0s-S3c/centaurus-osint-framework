"""
Unit tests for the Evidence Value Object.
"""

from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from centaurus.evidence.evidence import Evidence
from centaurus.evidence.evidence_source import EvidenceSource


def test_evidence_can_be_created():
    """
    An Evidence can be created.
    """

    timestamp = datetime.now()

    evidence = Evidence(
        source=EvidenceSource.WHOIS,
        data={
            "domain": "example.com",
        },
        collected_at=timestamp,
    )

    assert evidence is not None


def test_evidence_stores_source():
    """
    Evidence stores its origin.
    """

    evidence = Evidence(
        source=EvidenceSource.WHOIS,
        data={},
        collected_at=datetime.now(),
    )

    assert evidence.source == EvidenceSource.WHOIS


def test_evidence_stores_normalized_data():
    """
    Evidence stores normalized knowledge.
    """

    data = {
        "domain": "example.com",
        "registrar": "Example Registrar",
    }

    evidence = Evidence(
        source=EvidenceSource.WHOIS,
        data=data,
        collected_at=datetime.now(),
    )

    assert evidence.data == data


def test_evidence_stores_collection_timestamp():
    """
    Evidence stores the collection timestamp.
    """

    timestamp = datetime.now()

    evidence = Evidence(
        source=EvidenceSource.WHOIS,
        data={},
        collected_at=timestamp,
    )

    assert evidence.collected_at == timestamp


def test_evidence_is_immutable():
    """
    Evidence is immutable.
    """

    evidence = Evidence(
        source=EvidenceSource.WHOIS,
        data={},
        collected_at=datetime.now(),
    )

    with pytest.raises(FrozenInstanceError):
        evidence.source = EvidenceSource.RDAP


def test_evidence_instances_with_same_values_are_equal():
    """
    Evidence behaves as a Value Object.

    Equality depends on the values it contains,
    not on object identity.
    """

    timestamp = datetime.now()

    evidence1 = Evidence(
        source=EvidenceSource.WHOIS,
        data={
            "domain": "example.com",
        },
        collected_at=timestamp,
    )

    evidence2 = Evidence(
        source=EvidenceSource.WHOIS,
        data={
            "domain": "example.com",
        },
        collected_at=timestamp,
    )

    assert evidence1 == evidence2