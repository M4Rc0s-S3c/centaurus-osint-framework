"""
Unit tests for the RawObservation application object.
"""

from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from centaurus.evidence.evidence_source import EvidenceSource
from centaurus.evidence.raw_observation import RawObservation


def test_raw_observation_can_be_created():
    """
    A RawObservation can be created.
    """

    observation = RawObservation(
        source=EvidenceSource.WHOIS,
        data={
            "domain": "example.com",
        },
        collected_at=datetime.now(),
    )

    assert observation is not None


def test_raw_observation_stores_source():
    """
    RawObservation stores the tool that generated the observation.
    """

    observation = RawObservation(
        source=EvidenceSource.WHOIS,
        data={},
        collected_at=datetime.now(),
    )

    assert observation.source == EvidenceSource.WHOIS


def test_raw_observation_stores_raw_data():
    """
    RawObservation stores the raw knowledge produced by the plugin.
    """

    data = {
        "domain": "example.com",
        "registrar": "Example Registrar",
    }

    observation = RawObservation(
        source=EvidenceSource.WHOIS,
        data=data,
        collected_at=datetime.now(),
    )

    assert observation.data == data


def test_raw_observation_stores_collection_timestamp():
    """
    RawObservation stores the collection timestamp.
    """

    timestamp = datetime.now()

    observation = RawObservation(
        source=EvidenceSource.WHOIS,
        data={},
        collected_at=timestamp,
    )

    assert observation.collected_at == timestamp


def test_raw_observation_is_immutable():
    """
    RawObservation is immutable.
    """

    observation = RawObservation(
        source=EvidenceSource.WHOIS,
        data={},
        collected_at=datetime.now(),
    )

    with pytest.raises(FrozenInstanceError):
        observation.source = EvidenceSource.RDAP


def test_raw_observation_instances_with_same_values_are_equal():
    """
    RawObservation behaves as an immutable value container.
    """

    timestamp = datetime.now()

    observation1 = RawObservation(
        source=EvidenceSource.WHOIS,
        data={
            "domain": "example.com",
        },
        collected_at=timestamp,
    )

    observation2 = RawObservation(
        source=EvidenceSource.WHOIS,
        data={
            "domain": "example.com",
        },
        collected_at=timestamp,
    )

    assert observation1 == observation2