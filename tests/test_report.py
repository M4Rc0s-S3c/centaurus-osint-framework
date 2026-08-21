"""Tests for Report and ReportManager."""

from datetime import datetime, timezone

import pytest

from centaurus.evidence.evidence import Evidence
from centaurus.evidence.evidence_source import EvidenceSource
from centaurus.finding.finding import Finding
from centaurus.investigation import Investigation
from centaurus.investigation.exceptions import InvalidInvestigationState
from centaurus.report import Report, ReportManager
from centaurus.rules.condition import Condition
from centaurus.rules.rule import Rule


GENERATED_AT = datetime(2026, 8, 20, 12, 30, tzinfo=timezone.utc)


def create_finding(conclusion: str = "Test conclusion.") -> Finding:
    evidence = Evidence(
        source=EvidenceSource.WHOIS,
        data={"domain": "example.org"},
        collected_at=datetime.now(timezone.utc),
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


def create_report(
    investigation_id: str,
    findings: tuple[Finding, ...] = (),
    *,
    target: str = "example.org",
    analyst_question: str | None = None,
) -> Report:
    return Report(
        investigation_id=investigation_id,
        generated_at=GENERATED_AT,
        target=target,
        target_type="DOMAIN",
        intent="public_exposure_assessment",
        findings=findings,
        analyst_question=analyst_question,
    )


def test_report_is_immutable_value_object() -> None:
    investigation = Investigation(target="example.org", intent="public_exposure_assessment")
    report = create_report(investigation.id, analyst_question="Investiga example.org")

    assert report.investigation_id == investigation.id
    assert report.generated_at == GENERATED_AT
    assert report.target == "example.org"
    assert report.target_type == "DOMAIN"
    assert report.intent == "public_exposure_assessment"
    assert report.analyst_question == "Investiga example.org"
    assert report.findings == ()

    with pytest.raises(AttributeError):
        report.investigation_id = "other"  # type: ignore[misc]


def test_report_rejects_naive_generation_time() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        Report(
            investigation_id="INV-1",
            generated_at=datetime(2026, 8, 20, 12, 30),
            target="example.org",
            target_type="DOMAIN",
            intent="public_exposure_assessment",
            findings=(),
        )


def test_report_rejects_blank_analyst_question() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        create_report("INV-1", analyst_question="   ")


def test_report_manager_generates_report_with_context_and_all_supplied_findings() -> None:
    investigation = Investigation(target="example.org", intent="public_exposure_assessment")
    finding_one = create_finding("First conclusion.")
    finding_two = create_finding("Second conclusion.")
    investigation.add_finding(finding_one)
    investigation.add_finding(finding_two)

    report = ReportManager(clock=lambda: GENERATED_AT).generate(
        investigation=investigation,
        findings=(finding_one, finding_two),
        analyst_question="  Investiga la exposición pública de example.org  ",
    )

    assert isinstance(report, Report)
    assert report.investigation_id == investigation.id
    assert report.generated_at == GENERATED_AT
    assert report.target == "example.org"
    assert report.target_type == "DOMAIN"
    assert report.intent == "public_exposure_assessment"
    assert report.analyst_question == "Investiga la exposición pública de example.org"
    assert report.findings == (finding_one, finding_two)


def test_report_manager_accepts_empty_findings_and_missing_question() -> None:
    investigation = Investigation(target="example.org", intent="public_exposure_assessment")

    report = ReportManager(clock=lambda: GENERATED_AT).generate(
        investigation=investigation,
        findings=(),
    )

    assert report.findings == ()
    assert report.analyst_question is None


def test_report_manager_preserves_finding_order() -> None:
    investigation = Investigation(target="example.org", intent="public_exposure_assessment")
    finding_one = create_finding("First.")
    finding_two = create_finding("Second.")
    investigation.add_finding(finding_one)
    investigation.add_finding(finding_two)

    report = ReportManager(clock=lambda: GENERATED_AT).generate(
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
    report = create_report(investigation.id)

    investigation.add_report(report)

    assert investigation.report is report


def test_investigation_rejects_report_for_another_investigation() -> None:
    investigation = Investigation(target="example.org", intent="public_exposure_assessment")
    other = Investigation(target="example.net", intent="public_exposure_assessment")
    report = create_report(other.id, target="example.net")

    with pytest.raises(ValueError):
        investigation.add_report(report)


def test_investigation_rejects_second_report() -> None:
    investigation = Investigation(target="example.org", intent="public_exposure_assessment")
    first = create_report(investigation.id)
    second = create_report(investigation.id)

    investigation.add_report(first)

    with pytest.raises(InvalidInvestigationState):
        investigation.add_report(second)
