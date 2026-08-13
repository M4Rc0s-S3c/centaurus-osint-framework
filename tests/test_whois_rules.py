from datetime import datetime, timezone

from centaurus.evidence.evidence import Evidence
from centaurus.evidence.evidence_source import EvidenceSource
from centaurus.rules.rule_engine import RuleEngine
from centaurus.rules.whois_rules import RL_001, RL_002, WHOIS_RULES


def create_whois_evidence(data: dict) -> Evidence:
    return Evidence(
        source=EvidenceSource.WHOIS,
        data=data,
        collected_at=datetime.now(timezone.utc),
    )


def test_minimal_whois_rules_evaluate_normalized_evidence() -> None:
    evidence_one = create_whois_evidence(
        {
            "domain_name": "example.org",
            "registrar": "Example Registrar",
            "name_servers": ["ns1.example.org", "ns2.example.org"],
        }
    )
    evidence_two = create_whois_evidence(
        {
            "domain_name": "example.net",
            "registrar": None,
            "name_servers": ["ns1.example.net", "ns2.example.net"],
        }
    )
    evidence_three = create_whois_evidence(
        {
            "domain_name": "example.com",
            "registrar": None,
            "name_servers": None,
        }
    )

    engine = RuleEngine()

    findings_one = engine.evaluate(
        rules=WHOIS_RULES,
        evidences=(evidence_one,),
    )
    findings_two = engine.evaluate(
        rules=WHOIS_RULES,
        evidences=(evidence_two,),
    )
    findings_three = engine.evaluate(
        rules=WHOIS_RULES,
        evidences=(evidence_three,),
    )

    assert findings_one == ()
    assert [finding.rule.id for finding in findings_two] == [RL_001.id]
    assert [finding.rule.id for finding in findings_three] == [RL_001.id, RL_002.id]


def test_minimal_whois_rules_do_not_require_derived_temporal_fields() -> None:
    evidence = create_whois_evidence(
        {
            "domain_name": "example.com",
            "registrar": None,
            "name_servers": ["ns1.example.com"],
            "creation_date": "1995-08-14T04:00:00+00:00",
            "expiration_date": "2030-08-14T04:00:00+00:00",
        }
    )

    engine = RuleEngine()
    findings = engine.evaluate(
        rules=WHOIS_RULES,
        evidences=(evidence,),
    )

    assert [finding.rule.id for finding in findings] == [RL_001.id]
    assert "domain_age_days" not in evidence.data
    assert "days_until_expiration" not in evidence.data
