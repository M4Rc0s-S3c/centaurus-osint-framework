"""Tests for the deterministic Markdown projection of Report."""

from datetime import datetime, timezone

import pytest

from centaurus.evidence import Evidence, EvidenceSource
from centaurus.finding import Finding
from centaurus.persistence.report_markdown import render_report_markdown
from centaurus.report import Report
from centaurus.rules.condition import Condition
from centaurus.rules.rule import Rule


GENERATED_AT = datetime(2026, 8, 20, 12, 30, tzinfo=timezone.utc)


def make_report(*, analyst_question: str | None = "Analiza la exposición pública de example.org") -> Report:
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
    return Report(
        investigation_id="INV-MD-001",
        generated_at=GENERATED_AT,
        target="example.org",
        target_type="DOMAIN",
        intent="public_exposure_assessment",
        findings=(finding,),
        analyst_question=analyst_question,
    )


def test_markdown_projection_is_deterministic_traceable_and_analyst_friendly() -> None:
    report = make_report()

    first = render_report_markdown(report)
    second = render_report_markdown(report)

    assert first == second
    assert first.startswith("# CENTAURUS OSINT Investigation Report\n")
    assert "## Investigation context" in first
    assert "**Investigation ID:** `INV-MD-001`" in first
    assert "**Report generated:** `2026-08-20T12:30:00Z`" in first
    assert "**Target:** `DOMAIN:example.org`" in first
    assert "**Intent:** `public_exposure_assessment`" in first
    assert "## Analyst question" in first
    assert "> Analiza la exposición pública de example.org" in first
    assert "**Authoritative artifact:** `report.json`" in first
    assert "### F-001 — `RL-014` · `subdomain_corroborated_across_sources`" in first
    assert "#### Conclusion" in first
    assert report.findings[0].conclusion in first
    assert "`shared_collection_item_min_sources` 2" in first
    assert "##### Evidence 1 — `sublist3r`" in first
    assert "##### Evidence 2 — `crtsh`" in first
    assert '    "certificate_names": [' in first
    assert "2026-08-18T10:01:00+00:00" in first


def test_markdown_projection_quotes_multiline_analyst_question() -> None:
    report = make_report(
        analyst_question="Investiga example.org\n# No conviertas esto en encabezado",
    )

    rendered = render_report_markdown(report)

    assert "> Investiga example.org" in rendered
    assert "> # No conviertas esto en encabezado" in rendered
    assert "\n# No conviertas esto en encabezado\n" not in rendered


def test_markdown_projection_with_no_findings_or_question_is_explicit() -> None:
    report = Report(
        investigation_id="INV-EMPTY",
        generated_at=GENERATED_AT,
        target="203.0.113.10",
        target_type="IP",
        intent="public_exposure_assessment",
        findings=(),
        analyst_question=None,
    )

    rendered = render_report_markdown(report)

    assert "**Findings:** 0" in rendered
    assert "No analyst question was recorded for this Report." in rendered
    assert "No Findings were produced." in rendered


def test_markdown_projection_rejects_non_report() -> None:
    with pytest.raises(TypeError):
        render_report_markdown(object())  # type: ignore[arg-type]
