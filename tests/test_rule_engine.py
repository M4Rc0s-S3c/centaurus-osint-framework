"""
Unit tests for the RuleEngine component.
"""

from datetime import datetime, timezone

import pytest

from centaurus.evidence.evidence import Evidence
from centaurus.evidence.evidence_source import EvidenceSource
from centaurus.finding.finding import Finding
from centaurus.rules.condition import Condition
from centaurus.rules.rule import Rule
from centaurus.rules.rule_engine import RuleEngine


def create_rule(
    *,
    rule_id: str = "RL-001",
    version: str = "1.0",
    conditions: tuple[Condition, ...] | None = None,
    conclusion: str = "Test conclusion.",
) -> Rule:
    """
    Create a valid Rule for testing.
    """

    if conditions is None:
        conditions = (
            Condition(
                field="domain_age_days",
                operator="less_than",
                value=30,
            ),
        )

    return Rule(
        id=rule_id,
        version=version,
        name="test-rule",
        description="Test rule.",
        category="registration",
        conditions=conditions,
        conclusion=conclusion,
    )


def create_evidence(
    data: dict,
) -> Evidence:
    """
    Create valid Evidence for testing.
    """

    return Evidence(
        source=EvidenceSource.WHOIS,
        data=data,
        collected_at=datetime.now(),
    )


def test_rule_engine_can_be_created() -> None:
    """
    A RuleEngine can be instantiated.
    """

    engine = RuleEngine()

    assert isinstance(
        engine,
        RuleEngine,
    )


def test_rule_engine_requires_rules_tuple() -> None:
    """
    RuleEngine requires Rules to be supplied as a tuple.
    """

    engine = RuleEngine()

    evidence = create_evidence(
        {
            "domain_age_days": 10,
        }
    )

    with pytest.raises(TypeError):
        engine.evaluate(
            rules=[],
            evidences=(evidence,),
        )


def test_rule_engine_requires_evidences_tuple() -> None:
    """
    RuleEngine requires Evidence to be supplied as a tuple.
    """

    engine = RuleEngine()

    rule = create_rule()

    with pytest.raises(TypeError):
        engine.evaluate(
            rules=(rule,),
            evidences=[],
        )


def test_rule_engine_rejects_invalid_rule() -> None:
    """
    RuleEngine rejects objects that are not Rule instances.
    """

    engine = RuleEngine()

    evidence = create_evidence(
        {
            "domain_age_days": 10,
        }
    )

    with pytest.raises(TypeError):
        engine.evaluate(
            rules=("not a rule",),
            evidences=(evidence,),
        )


def test_rule_engine_rejects_invalid_evidence() -> None:
    """
    RuleEngine rejects objects that are not Evidence instances.
    """

    engine = RuleEngine()

    rule = create_rule()

    with pytest.raises(TypeError):
        engine.evaluate(
            rules=(rule,),
            evidences=("not evidence",),
        )


def test_rule_engine_returns_tuple() -> None:
    """
    RuleEngine always returns a tuple of Findings.
    """

    engine = RuleEngine()

    rule = create_rule()

    evidence = create_evidence(
        {
            "domain_age_days": 10,
        }
    )

    findings = engine.evaluate(
        rules=(rule,),
        evidences=(evidence,),
    )

    assert isinstance(
        findings,
        tuple,
    )


def test_rule_engine_returns_zero_findings_when_rule_does_not_match() -> None:
    """
    A valid evaluation may produce zero Findings.
    """

    engine = RuleEngine()

    rule = create_rule()

    evidence = create_evidence(
        {
            "domain_age_days": 60,
        }
    )

    findings = engine.evaluate(
        rules=(rule,),
        evidences=(evidence,),
    )

    assert findings == ()


def test_rule_engine_returns_one_finding_when_rule_matches() -> None:
    """
    A matching Rule produces one Finding.
    """

    engine = RuleEngine()

    rule = create_rule(
        conclusion="Domain is younger than 30 days.",
    )

    evidence = create_evidence(
        {
            "domain_age_days": 10,
        }
    )

    findings = engine.evaluate(
        rules=(rule,),
        evidences=(evidence,),
    )

    assert len(findings) == 1

    assert isinstance(
        findings[0],
        Finding,
    )


def test_rule_engine_finding_references_rule() -> None:
    """
    A produced Finding references the evaluated Rule.
    """

    engine = RuleEngine()

    rule = create_rule()

    evidence = create_evidence(
        {
            "domain_age_days": 10,
        }
    )

    findings = engine.evaluate(
        rules=(rule,),
        evidences=(evidence,),
    )

    assert findings[0].rule is rule


def test_rule_engine_finding_references_evidence() -> None:
    """
    A produced Finding references the Evidence
    that satisfied the Condition.
    """

    engine = RuleEngine()

    rule = create_rule()

    evidence = create_evidence(
        {
            "domain_age_days": 10,
        }
    )

    findings = engine.evaluate(
        rules=(rule,),
        evidences=(evidence,),
    )

    assert evidence in findings[0].evidences


def test_rule_engine_evaluates_multiple_rules() -> None:
    """
    RuleEngine evaluates multiple Rules.
    """

    engine = RuleEngine()

    rule_one = create_rule(
        rule_id="RL-001",
        conclusion="Domain is young.",
    )

    rule_two = create_rule(
        rule_id="RL-002",
        conclusion="Domain is recently registered.",
    )

    evidence = create_evidence(
        {
            "domain_age_days": 10,
        }
    )

    findings = engine.evaluate(
        rules=(
            rule_one,
            rule_two,
        ),
        evidences=(evidence,),
    )

    assert len(findings) == 2

    assert findings[0].rule is rule_one
    assert findings[1].rule is rule_two


def test_rule_engine_can_return_multiple_findings_from_one_rule() -> None:
    """
    A Rule with multiple matching Conditions can produce
    multiple Findings.
    """

    engine = RuleEngine()

    rule = create_rule(
        conditions=(
            Condition(
                field="registrar",
                operator="missing",
            ),
            Condition(
                field="creation_date",
                operator="missing",
            ),
        ),
        conclusion="Registration information is missing: {field}.",
    )

    evidence = create_evidence(
        {
            "domain": "example.org",
            "registrar": None,
            "creation_date": None,
        }
    )

    findings = engine.evaluate(
        rules=(rule,),
        evidences=(evidence,),
    )

    assert len(findings) == 2

    assert findings[0].rule is rule
    assert findings[1].rule is rule


def test_rule_engine_supports_equals() -> None:
    """
    RuleEngine supports the equals operator.
    """

    engine = RuleEngine()

    rule = create_rule(
        conditions=(
            Condition(
                field="dnssec",
                operator="equals",
                value=False,
            ),
        )
    )

    evidence = create_evidence(
        {
            "dnssec": False,
        }
    )

    findings = engine.evaluate(
        rules=(rule,),
        evidences=(evidence,),
    )

    assert len(findings) == 1


def test_rule_engine_supports_missing() -> None:
    """
    RuleEngine supports the missing operator.
    """

    engine = RuleEngine()

    rule = create_rule(
        conditions=(
            Condition(
                field="registrar",
                operator="missing",
            ),
        )
    )

    evidence = create_evidence(
        {
            "domain": "example.org",
            "registrar": None,
        }
    )

    findings = engine.evaluate(
        rules=(rule,),
        evidences=(evidence,),
    )

    assert len(findings) == 1


def test_rule_engine_supports_greater_than() -> None:
    """
    RuleEngine supports the greater_than operator.
    """

    engine = RuleEngine()

    rule = create_rule(
        conditions=(
            Condition(
                field="domain_age_days",
                operator="greater_than",
                value=30,
            ),
        )
    )

    evidence = create_evidence(
        {
            "domain_age_days": 60,
        }
    )

    findings = engine.evaluate(
        rules=(rule,),
        evidences=(evidence,),
    )

    assert len(findings) == 1


def test_rule_engine_supports_less_than_or_equal() -> None:
    """
    RuleEngine supports the less_than_or_equal operator.
    """

    engine = RuleEngine()

    rule = create_rule(
        conditions=(
            Condition(
                field="domain_age_days",
                operator="less_than_or_equal",
                value=30,
            ),
        )
    )

    evidence = create_evidence(
        {
            "domain_age_days": 30,
        }
    )

    findings = engine.evaluate(
        rules=(rule,),
        evidences=(evidence,),
    )

    assert len(findings) == 1


def test_rule_engine_supports_greater_than_or_equal() -> None:
    """
    RuleEngine supports the greater_than_or_equal operator.
    """

    engine = RuleEngine()

    rule = create_rule(
        conditions=(
            Condition(
                field="domain_age_days",
                operator="greater_than_or_equal",
                value=30,
            ),
        )
    )

    evidence = create_evidence(
        {
            "domain_age_days": 30,
        }
    )

    findings = engine.evaluate(
        rules=(rule,),
        evidences=(evidence,),
    )

    assert len(findings) == 1


def test_rule_engine_supports_collection_size_greater_than() -> None:
    """RuleEngine supports cardinality checks for normalized collections."""

    engine = RuleEngine()

    rule = create_rule(
        conditions=(
            Condition(
                field="subdomains",
                operator="collection_size_greater_than",
                value=1,
            ),
        )
    )

    evidence = create_evidence(
        {
            "subdomains": ["api.example.com", "www.example.com"],
        }
    )

    findings = engine.evaluate(
        rules=(rule,),
        evidences=(evidence,),
    )

    assert len(findings) == 1


def test_rule_engine_collection_size_greater_than_excludes_boundary() -> None:
    """Exactly the configured collection size does not satisfy > N."""

    engine = RuleEngine()

    rule = create_rule(
        conditions=(
            Condition(
                field="subdomains",
                operator="collection_size_greater_than",
                value=1,
            ),
        )
    )

    evidence = create_evidence(
        {
            "subdomains": ["www.example.com"],
        }
    )

    findings = engine.evaluate(
        rules=(rule,),
        evidences=(evidence,),
    )

    assert findings == ()


def test_rule_engine_collection_size_greater_than_ignores_non_collection() -> None:
    """Scalar or mapping values are not interpreted as normalized collections."""

    engine = RuleEngine()

    rule = create_rule(
        conditions=(
            Condition(
                field="subdomains",
                operator="collection_size_greater_than",
                value=1,
            ),
        )
    )

    for value in ("api.example.com", {"api.example.com": True}, None):
        findings = engine.evaluate(
            rules=(rule,),
            evidences=(create_evidence({"subdomains": value}),),
        )

        assert findings == ()


@pytest.mark.parametrize(
    "threshold",
    (1.0, True, "1"),
)
def test_rule_engine_collection_size_greater_than_requires_integer_threshold(
    threshold,
) -> None:
    """Collection cardinality uses a non-negative integer threshold."""

    engine = RuleEngine()

    rule = create_rule(
        conditions=(
            Condition(
                field="subdomains",
                operator="collection_size_greater_than",
                value=threshold,
            ),
        )
    )

    with pytest.raises(TypeError):
        engine.evaluate(
            rules=(rule,),
            evidences=(create_evidence({"subdomains": ["a", "b"]}),),
        )


def test_rule_engine_collection_size_greater_than_rejects_negative_threshold() -> None:
    """Collection cardinality rejects negative thresholds."""

    engine = RuleEngine()

    rule = create_rule(
        conditions=(
            Condition(
                field="subdomains",
                operator="collection_size_greater_than",
                value=-1,
            ),
        )
    )

    with pytest.raises(ValueError):
        engine.evaluate(
            rules=(rule,),
            evidences=(create_evidence({"subdomains": []}),),
        )


def test_rule_engine_rejects_unsupported_operator() -> None:
    """
    RuleEngine rejects unsupported operators.
    """

    engine = RuleEngine()

    rule = create_rule(
        conditions=(
            Condition(
                field="domain_age_days",
                operator="contains",
                value="30",
            ),
        )
    )

    evidence = create_evidence(
        {
            "domain_age_days": 10,
        }
    )

    with pytest.raises(
        ValueError,
        match="Unsupported Rule operator",
    ):
        engine.evaluate(
            rules=(rule,),
            evidences=(evidence,),
        )

def test_rule_engine_supports_age_less_than() -> None:
    engine = RuleEngine()
    rule = create_rule(
        conditions=(
            Condition(
                field="creation_date",
                operator="age_less_than",
                value=30,
            ),
        )
    )
    evidence = Evidence(
        source=EvidenceSource.WHOIS,
        data={"creation_date": "2026-07-20T00:00:00+00:00"},
        collected_at=datetime(2026, 8, 15, tzinfo=timezone.utc),
    )
    findings = engine.evaluate(rules=(rule,), evidences=(evidence,))
    assert len(findings) == 1


def test_rule_engine_age_less_than_excludes_exact_boundary() -> None:
    engine = RuleEngine()
    rule = create_rule(
        conditions=(
            Condition(
                field="creation_date",
                operator="age_less_than",
                value=30,
            ),
        )
    )
    evidence = Evidence(
        source=EvidenceSource.WHOIS,
        data={"creation_date": "2026-07-16T00:00:00+00:00"},
        collected_at=datetime(2026, 8, 15, tzinfo=timezone.utc),
    )
    findings = engine.evaluate(rules=(rule,), evidences=(evidence,))
    assert findings == ()


def test_rule_engine_supports_expires_within() -> None:
    engine = RuleEngine()
    rule = create_rule(
        conditions=(
            Condition(
                field="expiration_date",
                operator="expires_within",
                value=60,
            ),
        )
    )
    evidence = Evidence(
        source=EvidenceSource.WHOIS,
        data={"expiration_date": "2026-10-14T00:00:00+00:00"},
        collected_at=datetime(2026, 8, 15, tzinfo=timezone.utc),
    )
    findings = engine.evaluate(rules=(rule,), evidences=(evidence,))
    assert len(findings) == 1


def test_rule_engine_expires_within_includes_exact_boundary() -> None:
    engine = RuleEngine()
    rule = create_rule(
        conditions=(
            Condition(
                field="expiration_date",
                operator="expires_within",
                value=60,
            ),
        )
    )
    evidence = Evidence(
        source=EvidenceSource.WHOIS,
        data={"expiration_date": "2026-10-14T00:00:00+00:00"},
        collected_at=datetime(2026, 8, 15, tzinfo=timezone.utc),
    )
    findings = engine.evaluate(rules=(rule,), evidences=(evidence,))
    assert len(findings) == 1


def test_rule_engine_expires_within_does_not_flag_expired_value() -> None:
    engine = RuleEngine()
    rule = create_rule(
        conditions=(
            Condition(
                field="expiration_date",
                operator="expires_within",
                value=60,
            ),
        )
    )
    evidence = Evidence(
        source=EvidenceSource.WHOIS,
        data={"expiration_date": "2026-08-10T00:00:00+00:00"},
        collected_at=datetime(2026, 8, 15, tzinfo=timezone.utc),
    )
    findings = engine.evaluate(rules=(rule,), evidences=(evidence,))
    assert findings == ()


def test_rule_engine_supports_expired() -> None:
    engine = RuleEngine()
    rule = create_rule(
        conditions=(
            Condition(
                field="expiration_date",
                operator="expired",
            ),
        )
    )
    evidence = Evidence(
        source=EvidenceSource.WHOIS,
        data={"expiration_date": "2026-08-10T00:00:00+00:00"},
        collected_at=datetime(2026, 8, 15, tzinfo=timezone.utc),
    )
    findings = engine.evaluate(rules=(rule,), evidences=(evidence,))
    assert len(findings) == 1


def test_rule_engine_expired_does_not_flag_expiration_at_collection_time() -> None:
    engine = RuleEngine()
    rule = create_rule(
        conditions=(
            Condition(
                field="expiration_date",
                operator="expired",
            ),
        )
    )
    evidence = Evidence(
        source=EvidenceSource.WHOIS,
        data={"expiration_date": "2026-08-15T00:00:00+00:00"},
        collected_at=datetime(2026, 8, 15, tzinfo=timezone.utc),
    )
    findings = engine.evaluate(rules=(rule,), evidences=(evidence,))
    assert findings == ()


def test_rule_engine_age_less_than_does_not_flag_future_creation_date() -> None:
    engine = RuleEngine()
    rule = create_rule(
        conditions=(
            Condition(
                field="creation_date",
                operator="age_less_than",
                value=30,
            ),
        )
    )
    evidence = Evidence(
        source=EvidenceSource.WHOIS,
        data={"creation_date": "2026-08-20T00:00:00+00:00"},
        collected_at=datetime(2026, 8, 15, tzinfo=timezone.utc),
    )
    findings = engine.evaluate(rules=(rule,), evidences=(evidence,))
    assert findings == ()


def test_missing_condition_ignores_evidence_without_that_schema_field() -> None:
    """A Rule must not treat an unrelated Evidence schema as a missing value."""

    from centaurus.evidence import EvidenceSource

    evidence = Evidence(
        source=EvidenceSource.DNSRECON,
        data={"domain_name": "example.com", "a_records": ["192.0.2.10"]},
        collected_at=datetime(2026, 8, 16, tzinfo=timezone.utc),
    )
    rule = Rule(
        id="TEST-MISSING",
        version="1.0",
        name="registration field missing",
        description="test",
        category="test",
        conditions=(Condition(field="registrar", operator="missing"),),
        conclusion="registrar missing",
    )

    findings = RuleEngine().evaluate(rules=(rule,), evidences=(evidence,))

    assert findings == ()


def test_shared_collection_item_min_sources_requires_integer_threshold() -> None:
    rule = create_rule(
        conditions=(
            Condition(
                field="subdomains",
                operator="shared_collection_item_min_sources",
                value=2.0,
            ),
        ),
    )
    evidence = create_evidence({"subdomains": ["www.example.com"]})

    with pytest.raises(TypeError):
        RuleEngine().evaluate(
            rules=(rule,),
            evidences=(evidence,),
        )


def test_shared_collection_item_min_sources_requires_at_least_two_sources() -> None:
    rule = create_rule(
        conditions=(
            Condition(
                field="subdomains",
                operator="shared_collection_item_min_sources",
                value=1,
            ),
        ),
    )
    evidence = create_evidence({"subdomains": ["www.example.com"]})

    with pytest.raises(ValueError):
        RuleEngine().evaluate(
            rules=(rule,),
            evidences=(evidence,),
        )


def test_shared_collection_item_min_sources_expands_item_placeholder() -> None:
    rule = create_rule(
        conditions=(
            Condition(
                field="subdomains",
                operator="shared_collection_item_min_sources",
                value=2,
            ),
        ),
        conclusion="Corroborated item: {item}.",
    )
    first = Evidence(
        source=EvidenceSource.SUBLIST3R,
        data={"subdomains": ["www.example.com"]},
        collected_at=datetime.now(),
    )
    second = Evidence(
        source=EvidenceSource.CRTSH,
        data={"subdomains": ["www.example.com"]},
        collected_at=datetime.now(),
    )

    findings = RuleEngine().evaluate(
        rules=(rule,),
        evidences=(first, second),
    )

    assert len(findings) == 1
    assert findings[0].conclusion == "Corroborated item: www.example.com."
    assert findings[0].evidences == (first, second)
