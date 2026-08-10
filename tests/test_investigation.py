from datetime import datetime

import pytest

from centaurus.evidence.evidence import Evidence
from centaurus.evidence.evidence_source import EvidenceSource
from centaurus.finding.finding import Finding
from centaurus.rules.condition import Condition
from centaurus.investigation import (
    Investigation,
    InvestigationStatus,
)
from centaurus.investigation.exceptions import (
    InvalidInvestigationState,
)
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
        collected_at=datetime.now(),
    )


def create_condition() -> Condition:
    """
    Create a valid Condition for testing.
    """

    return Condition(
        field="domain_age_days",
        operator="less_than",
        value=30,
    )


def create_rule(
    name: str = "test_rule",
) -> Rule:
    """
    Create a valid Rule instance for testing.
    """

    return Rule(
        id="RL-TEST-001",
        version="1.0",
        name=name,
        description="Test rule.",
        category="whois_rdap",
        conditions=(
            create_condition(),
        ),
        conclusion="Test rule conclusion.",
    )


def create_finding(
    conclusion: str = "Test conclusion.",
) -> Finding:
    """
    Create a valid Finding instance for testing.
    """

    evidence = create_evidence(
        {
            "domain": "example.org",
        }
    )

    rule = create_rule()

    return Finding(
        conclusion=conclusion,
        rule=rule,
        evidences=(evidence,),
    )


def test_investigation_can_be_created() -> None:
    """
    An Investigation can be instantiated.
    """

    investigation = Investigation(
        objective="Investigate example.com",
    )

    assert isinstance(
        investigation,
        Investigation,
    )


def test_investigation_generates_identifier() -> None:
    """
    Every Investigation receives an identifier.
    """

    investigation = Investigation(
        objective="Investigate example.com",
    )

    assert investigation.id is not None
    assert investigation.id != ""


def test_investigation_stores_objective() -> None:
    """
    Investigation stores its objective.
    """

    objective = "Investigate example.com"

    investigation = Investigation(
        objective=objective,
    )

    assert investigation.objective == objective


def test_investigation_initial_status() -> None:
    """
    A new Investigation starts in CREATED state.
    """

    investigation = Investigation(
        objective="Investigate example.com",
    )

    assert (
        investigation.status
        is InvestigationStatus.CREATED
    )


def test_investigation_valid_lifecycle() -> None:
    """
    Investigation follows the valid lifecycle.
    """

    investigation = Investigation(
        objective="Investigate example.com",
    )

    investigation.mark_planned()

    assert (
        investigation.status
        is InvestigationStatus.PLANNED
    )

    investigation.mark_running()

    assert (
        investigation.status
        is InvestigationStatus.RUNNING
    )

    investigation.mark_completed()

    assert (
        investigation.status
        is InvestigationStatus.COMPLETED
    )


def test_investigation_can_fail_from_running() -> None:
    """
    Investigation can transition from RUNNING to FAILED.
    """

    investigation = Investigation(
        objective="Investigate example.com",
    )

    investigation.mark_planned()
    investigation.mark_running()
    investigation.mark_failed()

    assert (
        investigation.status
        is InvestigationStatus.FAILED
    )


def test_investigation_cannot_skip_planned() -> None:
    """
    Investigation cannot transition directly from CREATED to RUNNING.
    """

    investigation = Investigation(
        objective="Investigate example.com",
    )

    with pytest.raises(
        InvalidInvestigationState,
    ):
        investigation.mark_running()


def test_investigation_cannot_complete_before_running() -> None:
    """
    Investigation cannot complete before RUNNING.
    """

    investigation = Investigation(
        objective="Investigate example.com",
    )

    with pytest.raises(
        InvalidInvestigationState,
    ):
        investigation.mark_completed()


def test_completed_investigation_cannot_run_again() -> None:
    """
    Completed investigations cannot return to RUNNING.
    """

    investigation = Investigation(
        objective="Investigate example.com",
    )

    investigation.mark_planned()
    investigation.mark_running()
    investigation.mark_completed()

    with pytest.raises(
        InvalidInvestigationState,
    ):
        investigation.mark_running()


def test_investigation_can_store_evidence() -> None:
    """
    Investigation stores Evidence objects.
    """

    investigation = Investigation(
        objective="Investigate example.org",
    )

    evidence = Evidence(
        source=EvidenceSource.WHOIS,
        data={"domain": "example.org"},
        collected_at=datetime.now(),
    )

    investigation.add_evidence(evidence)

    assert len(investigation.evidence) == 1


def test_investigation_preserves_evidence_instance() -> None:
    """
    Investigation keeps the exact Evidence instance.
    """

    investigation = Investigation(
        objective="Investigate example.org",
    )

    evidence = Evidence(
        source=EvidenceSource.WHOIS,
        data={"domain": "example.org"},
        collected_at=datetime.now(),
    )

    investigation.add_evidence(evidence)

    assert investigation.evidence[0] is evidence


def test_investigation_accumulates_evidence() -> None:
    """
    Investigation accumulates Evidence objects.
    """

    investigation = Investigation(
        objective="Investigate example.org",
    )

    evidence1 = Evidence(
        source=EvidenceSource.WHOIS,
        data={"domain": "example.org"},
        collected_at=datetime.now(),
    )

    evidence2 = Evidence(
        source=EvidenceSource.RDAP,
        data={"domain": "example.org"},
        collected_at=datetime.now(),
    )

    investigation.add_evidence(evidence1)
    investigation.add_evidence(evidence2)

    assert len(investigation.evidence) == 2


def test_investigation_rejects_non_evidence() -> None:
    """
    Investigation only accepts Evidence objects.
    """

    investigation = Investigation(
        objective="Investigate example.org",
    )

    with pytest.raises(TypeError):
        investigation.add_evidence("not evidence")


def test_investigation_findings_are_initially_empty() -> None:
    """
    A new Investigation starts without Findings.
    """

    investigation = Investigation(
        objective="Investigate example.org",
    )

    assert investigation.findings == ()


def test_investigation_can_store_finding() -> None:
    """
    Investigation stores Finding objects.
    """

    investigation = Investigation(
        objective="Investigate example.org",
    )

    finding = create_finding()

    investigation.add_finding(finding)

    assert len(investigation.findings) == 1


def test_investigation_preserves_finding_instance() -> None:
    """
    Investigation keeps the exact Finding instance.
    """

    investigation = Investigation(
        objective="Investigate example.org",
    )

    finding = create_finding()

    investigation.add_finding(finding)

    assert investigation.findings[0] is finding


def test_investigation_accumulates_findings() -> None:
    """
    Investigation accumulates Finding objects.
    """

    investigation = Investigation(
        objective="Investigate example.org",
    )

    finding1 = create_finding(
        conclusion="First conclusion.",
    )

    finding2 = create_finding(
        conclusion="Second conclusion.",
    )

    investigation.add_finding(finding1)
    investigation.add_finding(finding2)

    assert len(investigation.findings) == 2


def test_investigation_findings_are_immutable_collection() -> None:
    """
    Investigation exposes Findings as an immutable tuple.
    """

    investigation = Investigation(
        objective="Investigate example.org",
    )

    finding = create_finding()

    investigation.add_finding(finding)

    assert isinstance(
        investigation.findings,
        tuple,
    )


def test_investigation_rejects_non_finding() -> None:
    """
    Investigation only accepts Finding objects.
    """

    investigation = Investigation(
        objective="Investigate example.org",
    )

    with pytest.raises(TypeError):
        investigation.add_finding("not a finding")