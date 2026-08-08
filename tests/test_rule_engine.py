"""
Unit tests for the RuleEngine component.
"""

from datetime import datetime

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
        category="whois_rdap",
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

    assert evidence in findings[0].evidence


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