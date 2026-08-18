"""Tests for factual public-exposure Rule definitions."""

from datetime import datetime, timezone

from centaurus.evidence import Evidence, EvidenceSource
from centaurus.rules.exposure_rules import (
    EXPOSURE_RULES,
    RL_008_MULTIPLE_PUBLIC_SUBDOMAINS_OBSERVED,
    RL_009_MULTIPLE_PUBLIC_EMAILS_OBSERVED,
    RL_014_SUBDOMAIN_CORROBORATED_ACROSS_SOURCES,
)
from centaurus.rules.rule_engine import RuleEngine


def create_evidence(
    source: EvidenceSource,
    data: dict,
) -> Evidence:
    return Evidence(
        source=source,
        data=data,
        collected_at=datetime(2026, 8, 18, tzinfo=timezone.utc),
    )


def test_exposure_rules_are_defined() -> None:
    subdomains_condition = RL_008_MULTIPLE_PUBLIC_SUBDOMAINS_OBSERVED.conditions[0]
    emails_condition = RL_009_MULTIPLE_PUBLIC_EMAILS_OBSERVED.conditions[0]
    correlation_condition = (
        RL_014_SUBDOMAIN_CORROBORATED_ACROSS_SOURCES.conditions[0]
    )

    assert RL_008_MULTIPLE_PUBLIC_SUBDOMAINS_OBSERVED.id == "RL-008"
    assert subdomains_condition.field == "subdomains"
    assert subdomains_condition.operator == "collection_size_greater_than"
    assert subdomains_condition.value == 1

    assert RL_009_MULTIPLE_PUBLIC_EMAILS_OBSERVED.id == "RL-009"
    assert emails_condition.field == "emails"
    assert emails_condition.operator == "collection_size_greater_than"
    assert emails_condition.value == 1

    assert RL_014_SUBDOMAIN_CORROBORATED_ACROSS_SOURCES.id == "RL-014"
    assert correlation_condition.field == "subdomains"
    assert correlation_condition.operator == "shared_collection_item_min_sources"
    assert correlation_condition.value == 2

    assert EXPOSURE_RULES == (
        RL_008_MULTIPLE_PUBLIC_SUBDOMAINS_OBSERVED,
        RL_009_MULTIPLE_PUBLIC_EMAILS_OBSERVED,
        RL_014_SUBDOMAIN_CORROBORATED_ACROSS_SOURCES,
    )


def test_rl_008_reports_multiple_public_subdomains() -> None:
    evidence = create_evidence(
        EvidenceSource.SUBLIST3R,
        {
            "domain_name": "example.com",
            "subdomains": ["api.example.com", "www.example.com"],
        },
    )

    findings = RuleEngine().evaluate(
        rules=(RL_008_MULTIPLE_PUBLIC_SUBDOMAINS_OBSERVED,),
        evidences=(evidence,),
    )

    assert len(findings) == 1
    assert findings[0].rule is RL_008_MULTIPLE_PUBLIC_SUBDOMAINS_OBSERVED
    assert findings[0].evidences == (evidence,)
    assert findings[0].conclusion == (
        "Multiple public subdomains were observed in normalized Evidence."
    )


def test_rl_008_does_not_report_single_public_subdomain() -> None:
    evidence = create_evidence(
        EvidenceSource.SUBLIST3R,
        {
            "domain_name": "example.com",
            "subdomains": ["www.example.com"],
        },
    )

    findings = RuleEngine().evaluate(
        rules=(RL_008_MULTIPLE_PUBLIC_SUBDOMAINS_OBSERVED,),
        evidences=(evidence,),
    )

    assert findings == ()


def test_rl_008_can_be_satisfied_by_multiple_normalized_sources() -> None:
    sublist3r_evidence = create_evidence(
        EvidenceSource.SUBLIST3R,
        {
            "domain_name": "example.com",
            "subdomains": ["api.example.com", "www.example.com"],
        },
    )
    crtsh_evidence = create_evidence(
        EvidenceSource.CRTSH,
        {
            "domain_name": "example.com",
            "subdomains": ["api.example.com", "mail.example.com"],
        },
    )
    theharvester_evidence = create_evidence(
        EvidenceSource.THEHARVESTER,
        {
            "domain_name": "example.com",
            "subdomains": ["mail.example.com", "www.example.com"],
        },
    )

    findings = RuleEngine().evaluate(
        rules=(RL_008_MULTIPLE_PUBLIC_SUBDOMAINS_OBSERVED,),
        evidences=(
            sublist3r_evidence,
            crtsh_evidence,
            theharvester_evidence,
        ),
    )

    assert len(findings) == 3
    assert [finding.evidences for finding in findings] == [
        (sublist3r_evidence,),
        (crtsh_evidence,),
        (theharvester_evidence,),
    ]


def test_rl_009_reports_multiple_public_emails() -> None:
    evidence = create_evidence(
        EvidenceSource.THEHARVESTER,
        {
            "domain_name": "example.com",
            "emails": ["admin@example.com", "security@example.com"],
        },
    )

    findings = RuleEngine().evaluate(
        rules=(RL_009_MULTIPLE_PUBLIC_EMAILS_OBSERVED,),
        evidences=(evidence,),
    )

    assert len(findings) == 1
    assert findings[0].rule is RL_009_MULTIPLE_PUBLIC_EMAILS_OBSERVED
    assert findings[0].evidences == (evidence,)
    assert findings[0].conclusion == (
        "Multiple public email addresses were observed in normalized Evidence."
    )


def test_rl_009_does_not_report_single_public_email() -> None:
    evidence = create_evidence(
        EvidenceSource.THEHARVESTER,
        {
            "domain_name": "example.com",
            "emails": ["security@example.com"],
        },
    )

    findings = RuleEngine().evaluate(
        rules=(RL_009_MULTIPLE_PUBLIC_EMAILS_OBSERVED,),
        evidences=(evidence,),
    )

    assert findings == ()


def test_exposure_rules_do_not_match_incompatible_schema() -> None:
    evidence = create_evidence(
        EvidenceSource.WHOIS,
        {
            "domain_name": "example.com",
            "registrar": "Example Registrar",
        },
    )

    findings = RuleEngine().evaluate(
        rules=EXPOSURE_RULES,
        evidences=(evidence,),
    )

    assert findings == ()


def test_rl_014_correlates_one_subdomain_across_two_sources() -> None:
    sublist3r_evidence = create_evidence(
        EvidenceSource.SUBLIST3R,
        {"subdomains": ["api.example.com", "www.example.com"]},
    )
    crtsh_evidence = create_evidence(
        EvidenceSource.CRTSH,
        {"subdomains": ["api.example.com", "mail.example.com"]},
    )

    findings = RuleEngine().evaluate(
        rules=(RL_014_SUBDOMAIN_CORROBORATED_ACROSS_SOURCES,),
        evidences=(sublist3r_evidence, crtsh_evidence),
    )

    assert len(findings) == 1
    assert findings[0].rule is RL_014_SUBDOMAIN_CORROBORATED_ACROSS_SOURCES
    assert findings[0].conclusion == (
        "Subdomain api.example.com was observed in at least two distinct "
        "normalized Evidence sources."
    )
    assert findings[0].evidences == (
        sublist3r_evidence,
        crtsh_evidence,
    )


def test_rl_014_keeps_all_distinct_supporting_sources() -> None:
    sublist3r_evidence = create_evidence(
        EvidenceSource.SUBLIST3R,
        {"subdomains": ["www.example.com"]},
    )
    crtsh_evidence = create_evidence(
        EvidenceSource.CRTSH,
        {"subdomains": ["www.example.com"]},
    )
    theharvester_evidence = create_evidence(
        EvidenceSource.THEHARVESTER,
        {"subdomains": ["www.example.com"]},
    )

    findings = RuleEngine().evaluate(
        rules=(RL_014_SUBDOMAIN_CORROBORATED_ACROSS_SOURCES,),
        evidences=(
            sublist3r_evidence,
            crtsh_evidence,
            theharvester_evidence,
        ),
    )

    assert len(findings) == 1
    assert findings[0].evidences == (
        sublist3r_evidence,
        crtsh_evidence,
        theharvester_evidence,
    )


def test_rl_014_does_not_count_repeated_evidence_source_twice() -> None:
    first_sublist3r_evidence = create_evidence(
        EvidenceSource.SUBLIST3R,
        {"subdomains": ["www.example.com"]},
    )
    second_sublist3r_evidence = create_evidence(
        EvidenceSource.SUBLIST3R,
        {"subdomains": ["www.example.com"]},
    )

    findings = RuleEngine().evaluate(
        rules=(RL_014_SUBDOMAIN_CORROBORATED_ACROSS_SOURCES,),
        evidences=(first_sublist3r_evidence, second_sublist3r_evidence),
    )

    assert findings == ()


def test_rl_014_produces_one_finding_per_shared_item_in_sorted_order() -> None:
    sublist3r_evidence = create_evidence(
        EvidenceSource.SUBLIST3R,
        {"subdomains": ["www.example.com", "api.example.com"]},
    )
    crtsh_evidence = create_evidence(
        EvidenceSource.CRTSH,
        {"subdomains": ["www.example.com", "api.example.com"]},
    )

    findings = RuleEngine().evaluate(
        rules=(RL_014_SUBDOMAIN_CORROBORATED_ACROSS_SOURCES,),
        evidences=(sublist3r_evidence, crtsh_evidence),
    )

    assert [finding.conclusion for finding in findings] == [
        "Subdomain api.example.com was observed in at least two distinct "
        "normalized Evidence sources.",
        "Subdomain www.example.com was observed in at least two distinct "
        "normalized Evidence sources.",
    ]


def test_rl_014_ignores_non_collection_and_non_string_items() -> None:
    invalid_collection = create_evidence(
        EvidenceSource.SUBLIST3R,
        {"subdomains": "www.example.com"},
    )
    mixed_collection = create_evidence(
        EvidenceSource.CRTSH,
        {"subdomains": [None, 123, "www.example.com"]},
    )
    other_source = create_evidence(
        EvidenceSource.THEHARVESTER,
        {"subdomains": ["mail.example.com"]},
    )

    findings = RuleEngine().evaluate(
        rules=(RL_014_SUBDOMAIN_CORROBORATED_ACROSS_SOURCES,),
        evidences=(invalid_collection, mixed_collection, other_source),
    )

    assert findings == ()
