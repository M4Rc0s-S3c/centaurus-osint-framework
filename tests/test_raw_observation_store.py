"""Tests for filesystem RAW persistence."""

import json
from datetime import datetime, timezone

import pytest

from centaurus.evidence import EvidenceSource, RawObservation
from centaurus.persistence import RawObservationStore
from centaurus.persistence.filesystem import FilesystemRawObservationStore


@pytest.fixture
def observation() -> RawObservation:
    return RawObservation(
        source=EvidenceSource.WHOIS,
        data={
            "domain": "example.com",
            "registrar": "Example Registrar",
            "created": datetime(2026, 8, 11, 12, 30, tzinfo=timezone.utc),
        },
        collected_at=datetime(2026, 8, 11, 12, 31, tzinfo=timezone.utc),
    )


def test_raw_observation_store_defines_persistence_contract():
    assert hasattr(RawObservationStore, "persist_raw")
    assert hasattr(FilesystemRawObservationStore, "persist_raw")


def test_persist_raw_creates_investigation_scoped_artifact(tmp_path, observation):
    store = FilesystemRawObservationStore(tmp_path)

    path = store.persist_raw("INV-001", observation)

    assert path == (
        tmp_path
        / "investigations"
        / "INV-001"
        / "evidences"
        / "raw"
        / "INV-001_0001-whois.json"
    )
    assert path.is_file()


def test_persist_raw_serializes_observation_contract(tmp_path, observation):
    store = FilesystemRawObservationStore(tmp_path)

    path = store.persist_raw("INV-001", observation)
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["source"] == "whois"
    assert payload["collected_at"] == "2026-08-11T12:31:00+00:00"
    assert payload["data"]["domain"] == "example.com"
    assert payload["data"]["created"] == "2026-08-11T12:30:00+00:00"


def test_persist_raw_allocates_monotonic_sequence(tmp_path, observation):
    store = FilesystemRawObservationStore(tmp_path)

    first = store.persist_raw("INV-001", observation)
    second = store.persist_raw("INV-001", observation)

    assert first.name == "INV-001_0001-whois.json"
    assert second.name == "INV-001_0002-whois.json"
    assert first.read_bytes() == second.read_bytes()


def test_persist_raw_sequence_is_global_across_sources(tmp_path, observation):
    """Sequence numbers advance across different tools in one Investigation."""

    store = FilesystemRawObservationStore(tmp_path)
    rdap_observation = RawObservation(
        source=EvidenceSource.RDAP,
        data={"ldhName": "example.com"},
        collected_at=observation.collected_at,
    )

    first = store.persist_raw("INV-001", observation)
    second = store.persist_raw("INV-001", rdap_observation)

    assert first.name == "INV-001_0001-whois.json"
    assert second.name == "INV-001_0002-rdap.json"

def test_persist_raw_never_overwrites_existing_artifact(tmp_path, observation):
    store = FilesystemRawObservationStore(tmp_path)
    raw_dir = tmp_path / "investigations" / "INV-001" / "evidences" / "raw"
    raw_dir.mkdir(parents=True)

    existing = raw_dir / "INV-001_0001-whois.json"
    existing.write_text("original", encoding="utf-8")

    path = store.persist_raw("INV-001", observation)

    assert path.name == "INV-001_0002-whois.json"
    assert existing.read_text(encoding="utf-8") == "original"


def test_persist_raw_rejects_invalid_observation(tmp_path):
    store = FilesystemRawObservationStore(tmp_path)

    with pytest.raises(TypeError, match="RawObservation"):
        store.persist_raw("INV-001", object())


def test_persist_raw_rejects_invalid_investigation_id(tmp_path, observation):
    store = FilesystemRawObservationStore(tmp_path)

    with pytest.raises(ValueError):
        store.persist_raw("../INV-001", observation)


def test_persist_raw_keeps_investigations_isolated(tmp_path, observation):
    store = FilesystemRawObservationStore(tmp_path)

    first = store.persist_raw("INV-001", observation)
    second = store.persist_raw("INV-002", observation)

    assert first.parent != second.parent
    assert first.name == "INV-001_0001-whois.json"
    assert second.name == "INV-002_0001-whois.json"
