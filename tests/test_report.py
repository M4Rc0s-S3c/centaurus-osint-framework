"""Tests for Report and ReportManager."""

from datetime import datetime

import pytest

from centaurus.evidence.evidence import Evidence
from centaurus.evidence.evidence_source import EvidenceSource
from centaurus.finding.finding import Finding
from centaurus.investigation import Investigation
from centaurus.investigation.exceptions import InvalidInvestigationState
from centaurus.report import Report, ReportManager
from centaurus.rules.condition import Condition
from centaurus.rules.rule import Rule


def create_finding(conclusion: str = "Test conclusion.") -> Finding:
    evidence = Evidence(
        source=EvidenceSource.WHOIS,
        data={"domain": "example.org"},
        collected_at=datetime.now(),
    )
    rule = Rule(
        id="RL-TEST-001",
        version="1.0",
        name="test_rule",
        description="Test rule.",
        category="registration",
        conditions=(
            Condition(
                field="domain",
                operator="equals",
                value="example.org",
            ),
        ),
        conclusion=conclusion,
    )
    return Finding(
        conclusion=conclusion,
        rule=rule,
        evidences=(evidence,),
    )


def test_report_is_immutable_value_object() -> None:
    investigation = Investigation(target="example.org", intent="public_exposure_assessment")
    report = Report(investigation_id=investigation.id, findings=())

    assert report.investigation_id == investigation.id
    assert report.findings == ()

    with pytest.raises(AttributeError):
        report.investigation_id = "other"  # type: ignore[misc]


def test_report_manager_generates_report_with_all_supplied_findings() -> None:
    investigation = Investigation(target="example.org", intent="public_exposure_assessment")
    finding_one = create_finding("First conclusion.")
    finding_two = create_finding("Second conclusion.")
    investigation.add_finding(finding_one)
    investigation.add_finding(finding_two)

    report = ReportManager().generate(
        investigation=investigation,
        findings=(finding_one, finding_two),
    )

    assert isinstance(report, Report)
    assert report.investigation_id == investigation.id
    assert report.findings == (finding_one, finding_two)


def test_report_manager_accepts_empty_findings() -> None:
    investigation = Investigation(target="example.org", intent="public_exposure_assessment")

    report = ReportManager().generate(
        investigation=investigation,
        findings=(),
    )

    assert report.findings == ()


def test_report_manager_preserves_finding_order() -> None:
    investigation = Investigation(target="example.org", intent="public_exposure_assessment")
    finding_one = create_finding("First.")
    finding_two = create_finding("Second.")
    investigation.add_finding(finding_one)
    investigation.add_finding(finding_two)

    report = ReportManager().generate(
        investigation=investigation,
        findings=(finding_two, finding_one),
    )

    assert report.findings == (finding_two, finding_one)


def test_report_manager_rejects_non_tuple_findings() -> None:
    investigation = Investigation(target="example.org", intent="public_exposure_assessment")

    with pytest.raises(TypeError):
        ReportManager().generate(
            investigation=investigation,
            findings=[],  # type: ignore[arg-type]
        )


def test_report_manager_rejects_finding_from_another_investigation() -> None:
    investigation = Investigation(target="example.org", intent="public_exposure_assessment")
    other_investigation = Investigation(target="example.net", intent="public_exposure_assessment")
    finding = create_finding()
    other_investigation.add_finding(finding)

    with pytest.raises(ValueError):
        ReportManager().generate(
            investigation=investigation,
            findings=(finding,),
        )


def test_investigation_integrates_one_report() -> None:
    investigation = Investigation(target="example.org", intent="public_exposure_assessment")
    report = Report(investigation_id=investigation.id, findings=())

    investigation.add_report(report)

    assert investigation.report is report


def test_investigation_rejects_report_for_another_investigation() -> None:
    investigation = Investigation(target="example.org", intent="public_exposure_assessment")
    other = Investigation(target="example.net", intent="public_exposure_assessment")
    report = Report(investigation_id=other.id, findings=())

    with pytest.raises(ValueError):
        investigation.add_report(report)


def test_investigation_rejects_second_report() -> None:
    investigation = Investigation(target="example.org", intent="public_exposure_assessment")
    first = Report(investigation_id=investigation.id, findings=())
    second = Report(investigation_id=investigation.id, findings=())

    investigation.add_report(first)

    with pytest.raises(InvalidInvestigationState):
        investigation.add_report(second)
