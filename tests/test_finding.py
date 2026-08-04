"""
Tests for the Finding domain object.
"""

from datetime import datetime, timezone

import pytest

from centaurus.evidence.evidence import Evidence
from centaurus.evidence.evidence_source import EvidenceSource
from centaurus.finding.finding import Finding
from centaurus.rules.rule import Rule


def create_evidence(
    data: dict,
) -> Evidence:
    """
    Create a valid Evidence instance for testing.
    """

    return Evidence(
        source=EvidenceSource.WHOIS,
        data=data,
        collected_at=datetime.now(timezone.utc),
    )


def create_rule(
    name: str = "test_rule",
) -> Rule:
    """
    Create a valid Rule instance for testing.
    """

    return Rule(
        name=name,
        description="Test rule.",
    )


def test_finding_can_be_created() -> None:
    """
    A Finding can be created from a conclusion,
    one Rule and one or more Evidence objects.
    """

    evidence = create_evidence(
        {
            "domain_name": "example.org",
        }
    )

    rule = create_rule()

    finding = Finding(
        conclusion="The domain has a WHOIS record.",
        rule=rule,
        evidences=(evidence,),
    )

    assert finding.conclusion == (
        "The domain has a WHOIS record."
    )

    assert finding.rule is rule

    assert finding.evidences == (evidence,)


def test_finding_is_immutable() -> None:
    """
    Finding is an immutable Value Object.
    """

    evidence = create_evidence(
        {
            "domain_name": "example.org",
        }
    )

    rule = create_rule()

    finding = Finding(
        conclusion="The domain has a WHOIS record.",
        rule=rule,
        evidences=(evidence,),
    )

    with pytest.raises(AttributeError):
        finding.conclusion = "Modified conclusion"


def test_finding_supports_multiple_evidences() -> None:
    """
    A Finding may be supported by multiple Evidence objects.
    """

    evidence_one = create_evidence(
        {
            "domain_name": "example.org",
        }
    )

    evidence_two = create_evidence(
        {
            "registrar": "ICANN",
        }
    )

    rule = create_rule()

    finding = Finding(
        conclusion="The domain has a WHOIS registration.",
        rule=rule,
        evidences=(
            evidence_one,
            evidence_two,
        ),
    )

    assert finding.evidences == (
        evidence_one,
        evidence_two,
    )


def test_finding_evidences_are_immutable() -> None:
    """
    The Evidence collection exposed by Finding cannot be modified.
    """

    evidence = create_evidence(
        {
            "domain_name": "example.org",
        }
    )

    rule = create_rule()

    finding = Finding(
        conclusion="The domain has a WHOIS record.",
        rule=rule,
        evidences=(evidence,),
    )

    assert isinstance(finding.evidences, tuple)

    with pytest.raises(AttributeError):
        finding.evidences += (evidence,)

