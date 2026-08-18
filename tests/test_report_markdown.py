"""Tests for the deterministic Markdown projection of Report."""

from datetime import datetime, timezone

import pytest

from centaurus.evidence import Evidence, EvidenceSource
from centaurus.finding import Finding
from centaurus.persistence.report_markdown import render_report_markdown
from centaurus.report import Report
from centaurus.rules.condition import Condition
from centaurus.rules.rule import Rule


def make_report() -> Report:
    first = Evidence(
        source=EvidenceSource.SUBLIST3R,
        data={"subdomains": ["api.example.org", "www.example.org"]},
        collected_at=datetime(2026, 8, 18, 10, 0, tzinfo=timezone.utc),
    )
    second = Evidence(
        source=EvidenceSource.CRTSH,
        data={"subdomains": ["www.example.org"], "certificate_names": ["www.example.org"]},
        collected_at=datetime(2026, 8, 18, 10, 1, tzinfo=timezone.utc),
    )
    rule = Rule(
        id="RL-014",
        version="1.0",
        name="subdomain_corroborated_across_sources",
        description="Detect a subdomain observed by at least two distinct sources.",
        category="public_exposure",
        conditions=(
            Condition(
                field="subdomains",
                operator="shared_collection_item_min_sources",
                value=2,
            ),
        ),
        conclusion=(
            "Subdomain www.example.org was observed in at least two distinct "
            "normalized Evidence sources."
        ),
    )
    finding = Finding(
        conclusion=rule.conclusion,
        rule=rule,
        evidences=(first, second),
    )
    return Report(investigation_id="INV-MD-001", findings=(finding,))


def test_markdown_projection_is_deterministic_and_traceable() -> None:
    report = make_report()

    first = render_report_markdown(report)
    second = render_report_markdown(report)

    assert first == second
    assert first.startswith("# CENTAURUS Report\n")
    assert "**Investigation ID:** `INV-MD-001`" in first
    assert "**Authoritative artifact:** `report.json`" in first
    assert "### Finding 1 — `RL-014`" in first
    assert report.findings[0].conclusion in first
    assert "`shared_collection_item_min_sources` 2" in first
    assert "##### Evidence 1 — `sublist3r`" in first
    assert "##### Evidence 2 — `crtsh`" in first
    assert '    "certificate_names": [' in first
    assert "2026-08-18T10:01:00+00:00" in first


def test_markdown_projection_with_no_findings_is_explicit() -> None:
    report = Report(investigation_id="INV-EMPTY", findings=())

    rendered = render_report_markdown(report)

    assert "**Findings:** 0" in rendered
    assert "No Findings were produced." in rendered


def test_markdown_projection_rejects_non_report() -> None:
    with pytest.raises(TypeError):
        render_report_markdown(object())  # type: ignore[arg-type]
