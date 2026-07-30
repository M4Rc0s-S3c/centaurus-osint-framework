"""
Tests del contrato funcional de EvidenceManager.

Estos tests verifican únicamente el comportamiento esperado del componente
desde el punto de vista del dominio.

No prueban detalles de implementación.
"""

import pytest

from centaurus.evidence.evidence import Evidence
from centaurus.evidence.evidence_manager import EvidenceManager


def test_create_evidence_returns_evidence():
    """
    Dada una Raw Observation válida, EvidenceManager debe devolver
    una instancia de Evidence.
    """

    manager = EvidenceManager()

    raw_observation = {
        "plugin": "whois_lookup",
        "timestamp": "2026-07-30T10:00:00Z",
        "data": {
            "domain": "example.org"
        }
    }

    evidence = manager.create_evidence(raw_observation)

    assert isinstance(evidence, Evidence)


def test_created_evidence_is_immutable():
    """
    Toda Evidence creada por EvidenceManager debe respetar el contrato
    de inmutabilidad definido por el dominio.
    """

    manager = EvidenceManager()

    raw_observation = {
        "plugin": "whois_lookup",
        "timestamp": "2026-07-30T10:00:00Z",
        "data": {
            "domain": "example.org"
        }
    }

    evidence = manager.create_evidence(raw_observation)

    with pytest.raises(AttributeError):
        evidence.data = {}


def test_create_evidence_requires_raw_observation():
    """
    EvidenceManager únicamente puede construir Evidence a partir
    de una Raw Observation válida.
    """

    manager = EvidenceManager()

    with pytest.raises(ValueError):
        manager.create_evidence(None)


def test_create_evidence_preserves_observed_knowledge():
    """
    El conocimiento observado debe conservarse durante la creación
    de la Evidence.
    """

    manager = EvidenceManager()

    raw_observation = {
        "plugin": "whois_lookup",
        "timestamp": "2026-07-30T10:00:00Z",
        "data": {
            "domain": "example.org"
        }
    }

    evidence = manager.create_evidence(raw_observation)

    assert evidence is not None


def test_create_evidence_is_deterministic():
    """
    La misma observación debe producir una representación equivalente
    de Evidence.
    """

    manager = EvidenceManager()

    raw_observation = {
        "plugin": "whois_lookup",
        "timestamp": "2026-07-30T10:00:00Z",
        "data": {
            "domain": "example.org"
        }
    }

    evidence1 = manager.create_evidence(raw_observation)
    evidence2 = manager.create_evidence(raw_observation)

    assert evidence1 == evidence2