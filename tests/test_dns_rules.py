"""Tests for DNS rule definitions."""

from datetime import datetime, timezone

from centaurus.evidence import Evidence, EvidenceSource
from centaurus.rules.dns_rules import (
    DNS_RULES,
    RL_007_SPF_POLICY_NOT_OBSERVED,
    RL_010_DIRECT_DMARC_POLICY_NOT_OBSERVED,
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


def test_dns_rules_are_defined() -> None:
    assert RL_007_SPF_POLICY_NOT_OBSERVED.id == "RL-007"
    assert RL_007_SPF_POLICY_NOT_OBSERVED.conditions[0].field == "spf_records"
    assert RL_007_SPF_POLICY_NOT_OBSERVED.conditions[0].operator == "equals"
    assert RL_007_SPF_POLICY_NOT_OBSERVED.conditions[0].value == []

    assert RL_010_DIRECT_DMARC_POLICY_NOT_OBSERVED.id == "RL-010"
    assert RL_010_DIRECT_DMARC_POLICY_NOT_OBSERVED.conditions[0].field == "dmarc_records"
    assert RL_010_DIRECT_DMARC_POLICY_NOT_OBSERVED.conditions[0].operator == "equals"
    assert RL_010_DIRECT_DMARC_POLICY_NOT_OBSERVED.conditions[0].value == []

    assert DNS_RULES == (
        RL_007_SPF_POLICY_NOT_OBSERVED,
        RL_010_DIRECT_DMARC_POLICY_NOT_OBSERVED,
    )


def test_rl_007_reports_spf_policy_not_observed() -> None:
    evidence = create_evidence(
        EvidenceSource.DNSRECON,
        {
            "domain_name": "example.com",
            "spf_records": [],
        },
    )

    findings = RuleEngine().evaluate(
        rules=(RL_007_SPF_POLICY_NOT_OBSERVED,),
        evidences=(evidence,),
    )

    assert len(findings) == 1
    assert findings[0].rule is RL_007_SPF_POLICY_NOT_OBSERVED
    assert findings[0].evidences == (evidence,)
    assert findings[0].conclusion == (
        "No SPF policy was observed in the normalized DNS evidence."
    )


def test_rl_007_does_not_report_when_spf_policy_is_observed() -> None:
    evidence = create_evidence(
        EvidenceSource.DNSRECON,
        {
            "domain_name": "example.com",
            "spf_records": ["v=spf1 -all"],
        },
    )

    findings = RuleEngine().evaluate(
        rules=(RL_007_SPF_POLICY_NOT_OBSERVED,),
        evidences=(evidence,),
    )

    assert findings == ()


def test_rl_007_does_not_report_when_spf_field_is_not_in_schema() -> None:
    evidence = create_evidence(
        EvidenceSource.WHOIS,
        {
            "domain_name": "example.com",
            "registrar": "Example Registrar",
        },
    )

    findings = RuleEngine().evaluate(
        rules=(RL_007_SPF_POLICY_NOT_OBSERVED,),
        evidences=(evidence,),
    )

    assert findings == ()


def test_rl_007_only_references_the_matching_dns_evidence() -> None:
    registral_evidence = create_evidence(
        EvidenceSource.RDAP,
        {
            "domain_name": "example.com",
            "registrar": "Example Registrar",
        },
    )
    dns_evidence = create_evidence(
        EvidenceSource.DNSRECON,
        {
            "domain_name": "example.com",
            "spf_records": [],
        },
    )

    findings = RuleEngine().evaluate(
        rules=(RL_007_SPF_POLICY_NOT_OBSERVED,),
        evidences=(registral_evidence, dns_evidence),
    )

    assert len(findings) == 1
    assert findings[0].evidences == (dns_evidence,)


def test_rl_010_reports_direct_dmarc_policy_not_observed() -> None:
    evidence = create_evidence(
        EvidenceSource.DNSRECON,
        {
            "domain_name": "example.com",
            "query_name": "_dmarc.example.com",
            "dmarc_records": [],
        },
    )

    findings = RuleEngine().evaluate(
        rules=(RL_010_DIRECT_DMARC_POLICY_NOT_OBSERVED,),
        evidences=(evidence,),
    )

    assert len(findings) == 1
    assert findings[0].rule is RL_010_DIRECT_DMARC_POLICY_NOT_OBSERVED
    assert findings[0].evidences == (evidence,)
    assert findings[0].conclusion == (
        "No direct DMARC policy record was observed at the target domain's "
        "_dmarc DNS name."
    )


def test_rl_010_does_not_report_when_direct_dmarc_policy_is_observed() -> None:
    evidence = create_evidence(
        EvidenceSource.DNSRECON,
        {
            "domain_name": "example.com",
            "query_name": "_dmarc.example.com",
            "dmarc_records": ["v=DMARC1; p=reject"],
        },
    )

    findings = RuleEngine().evaluate(
        rules=(RL_010_DIRECT_DMARC_POLICY_NOT_OBSERVED,),
        evidences=(evidence,),
    )

    assert findings == ()


def test_rl_010_does_not_report_for_standard_dns_schema() -> None:
    evidence = create_evidence(
        EvidenceSource.DNSRECON,
        {
            "domain_name": "example.com",
            "spf_records": [],
        },
    )

    findings = RuleEngine().evaluate(
        rules=(RL_010_DIRECT_DMARC_POLICY_NOT_OBSERVED,),
        evidences=(evidence,),
    )

    assert findings == ()


def test_dns_rules_remain_isolated_between_standard_and_dmarc_evidence() -> None:
    standard_evidence = create_evidence(
        EvidenceSource.DNSRECON,
        {
            "domain_name": "example.com",
            "spf_records": [],
        },
    )
    dmarc_evidence = create_evidence(
        EvidenceSource.DNSRECON,
        {
            "domain_name": "example.com",
            "query_name": "_dmarc.example.com",
            "dmarc_records": [],
        },
    )

    findings = RuleEngine().evaluate(
        rules=DNS_RULES,
        evidences=(standard_evidence, dmarc_evidence),
    )

    assert [finding.rule.id for finding in findings] == ["RL-007", "RL-010"]
    assert findings[0].evidences == (standard_evidence,)
    assert findings[1].evidences == (dmarc_evidence,)
