"""
Tests for the WHOIS/RDAP rule definitions.
"""

from datetime import datetime, timezone

from centaurus.evidence import Evidence, EvidenceSource
from centaurus.rules.rule_engine import RuleEngine
from centaurus.rules.whois_rules import (
    RL_001_MISSING_REGISTRAR,
    RL_002_MISSING_NAME_SERVERS,
    RL_003_INCOMPLETE_REGISTRATION_INFORMATION,
    RL_004_DNSSEC_STATUS_OBSERVED,
    RL_005_REGISTRANT_NAME_UNAVAILABLE,
    WHOIS_RULES,
)


def create_whois_evidence(data: dict) -> Evidence:
    return Evidence(
        source=EvidenceSource.WHOIS,
        data=data,
        collected_at=datetime(2026, 8, 13, tzinfo=timezone.utc),
    )


def test_whois_rules_are_defined() -> None:
    assert RL_001_MISSING_REGISTRAR.id == "RL-001"
    assert RL_002_MISSING_NAME_SERVERS.id == "RL-002"
    assert RL_003_INCOMPLETE_REGISTRATION_INFORMATION.id == "RL-003"
    assert RL_004_DNSSEC_STATUS_OBSERVED.id == "RL-004"
    assert RL_005_REGISTRANT_NAME_UNAVAILABLE.id == "RL-005"
    assert WHOIS_RULES == (
        RL_001_MISSING_REGISTRAR,
        RL_002_MISSING_NAME_SERVERS,
        RL_003_INCOMPLETE_REGISTRATION_INFORMATION,
        RL_004_DNSSEC_STATUS_OBSERVED,
        RL_005_REGISTRANT_NAME_UNAVAILABLE,
    )


def test_minimal_whois_rules_evaluate_normalized_evidence() -> None:
    evidence_one = create_whois_evidence({
        "domain_name": "example.org",
        "registrar": "Example Registrar",
        "name_servers": ["ns1.example.org", "ns2.example.org"],
        "creation_date": "2020-01-01T00:00:00+00:00",
        "expiration_date": "2030-01-01T00:00:00+00:00",
        "dnssec": "signedDelegation",
    })
    evidence_two = create_whois_evidence({
        "domain_name": "example.net",
        "registrar": None,
        "name_servers": ["ns1.example.net", "ns2.example.net"],
        "creation_date": "2020-01-01T00:00:00+00:00",
        "expiration_date": "2030-01-01T00:00:00+00:00",
        "dnssec": "unsigned",
    })
    evidence_three = create_whois_evidence({
        "domain_name": "example.com",
        "registrar": None,
        "name_servers": None,
        "creation_date": None,
        "expiration_date": None,
        "dnssec": None,
    })

    findings = RuleEngine().evaluate(
        rules=WHOIS_RULES,
        evidences=(evidence_one, evidence_two, evidence_three),
    )

    assert [finding.rule.id for finding in findings] == [
        "RL-001",
        "RL-001",
        "RL-002",
        "RL-003",
        "RL-003",
        "RL-004",
        "RL-004",
        "RL-005",
        "RL-005",
        "RL-005",
    ]


def test_rl_003_reports_missing_creation_date() -> None:
    evidence = create_whois_evidence({
        "domain_name": "example.org",
        "registrar": "Example Registrar",
        "name_servers": ["ns1.example.org"],
        "creation_date": None,
        "expiration_date": "2030-01-01T00:00:00+00:00",
    })

    findings = RuleEngine().evaluate(
        rules=(RL_003_INCOMPLETE_REGISTRATION_INFORMATION,),
        evidences=(evidence,),
    )

    assert len(findings) == 1
    assert findings[0].rule is RL_003_INCOMPLETE_REGISTRATION_INFORMATION
    assert findings[0].evidences == (evidence,)


def test_rl_003_reports_missing_expiration_date() -> None:
    evidence = create_whois_evidence({
        "domain_name": "example.org",
        "registrar": "Example Registrar",
        "name_servers": ["ns1.example.org"],
        "creation_date": "2020-01-01T00:00:00+00:00",
        "expiration_date": None,
    })

    findings = RuleEngine().evaluate(
        rules=(RL_003_INCOMPLETE_REGISTRATION_INFORMATION,),
        evidences=(evidence,),
    )

    assert len(findings) == 1
    assert findings[0].rule is RL_003_INCOMPLETE_REGISTRATION_INFORMATION
    assert findings[0].evidences == (evidence,)


def test_rl_003_can_produce_multiple_findings_for_missing_registration_dates() -> None:
    evidence = create_whois_evidence({
        "domain_name": "example.org",
        "registrar": "Example Registrar",
        "name_servers": ["ns1.example.org"],
        "creation_date": None,
        "expiration_date": None,
    })

    findings = RuleEngine().evaluate(
        rules=(RL_003_INCOMPLETE_REGISTRATION_INFORMATION,),
        evidences=(evidence,),
    )

    assert len(findings) == 2
    assert [finding.rule.id for finding in findings] == ["RL-003", "RL-003"]
    assert all(finding.evidences == (evidence,) for finding in findings)


def test_rl_004_reports_signed_delegation() -> None:
    evidence = create_whois_evidence({
        "domain_name": "example.org",
        "dnssec": "signedDelegation",
    })

    findings = RuleEngine().evaluate(
        rules=(RL_004_DNSSEC_STATUS_OBSERVED,),
        evidences=(evidence,),
    )

    assert len(findings) == 1
    assert findings[0].rule is RL_004_DNSSEC_STATUS_OBSERVED
    assert findings[0].evidences == (evidence,)


def test_rl_004_reports_unsigned_status() -> None:
    evidence = create_whois_evidence({
        "domain_name": "example.org",
        "dnssec": "unsigned",
    })

    findings = RuleEngine().evaluate(
        rules=(RL_004_DNSSEC_STATUS_OBSERVED,),
        evidences=(evidence,),
    )

    assert len(findings) == 1
    assert findings[0].rule is RL_004_DNSSEC_STATUS_OBSERVED
    assert findings[0].evidences == (evidence,)


def test_rl_004_does_not_create_finding_when_dnssec_is_missing() -> None:
    evidence = create_whois_evidence({
        "domain_name": "example.org",
        "dnssec": None,
    })

    findings = RuleEngine().evaluate(
        rules=(RL_004_DNSSEC_STATUS_OBSERVED,),
        evidences=(evidence,),
    )

    assert findings == ()


def test_rl_005_reports_missing_registrant_name() -> None:
    evidence = create_whois_evidence({
        "domain_name": "example.org",
        "registrant_name": None,
    })

    findings = RuleEngine().evaluate(
        rules=(RL_005_REGISTRANT_NAME_UNAVAILABLE,),
        evidences=(evidence,),
    )

    assert len(findings) == 1
    assert findings[0].rule is RL_005_REGISTRANT_NAME_UNAVAILABLE
    assert findings[0].evidences == (evidence,)


def test_rl_005_reports_redacted_registrant_name() -> None:
    evidence = create_whois_evidence({
        "domain_name": "example.org",
        "registrant_name": "[REDACTED]",
    })

    findings = RuleEngine().evaluate(
        rules=(RL_005_REGISTRANT_NAME_UNAVAILABLE,),
        evidences=(evidence,),
    )

    assert len(findings) == 1
    assert findings[0].rule is RL_005_REGISTRANT_NAME_UNAVAILABLE
    assert findings[0].evidences == (evidence,)


def test_rl_005_does_not_flag_available_registrant_name() -> None:
    evidence = create_whois_evidence({
        "domain_name": "example.org",
        "registrant_name": "Example Person",
    })

    findings = RuleEngine().evaluate(
        rules=(RL_005_REGISTRANT_NAME_UNAVAILABLE,),
        evidences=(evidence,),
    )

    assert findings == ()


def test_rl_005_does_not_change_existing_rule_count_or_semantics() -> None:
    evidence = create_whois_evidence({
        "domain_name": "example.org",
        "registrar": "Example Registrar",
        "name_servers": ["ns1.example.org"],
        "creation_date": "2020-01-01T00:00:00+00:00",
        "expiration_date": "2030-01-01T00:00:00+00:00",
        "dnssec": "signedDelegation",
        "registrant_name": "[REDACTED]",
    })

    findings = RuleEngine().evaluate(
        rules=WHOIS_RULES,
        evidences=(evidence,),
    )

    assert [finding.rule.id for finding in findings] == ["RL-004", "RL-005"]
