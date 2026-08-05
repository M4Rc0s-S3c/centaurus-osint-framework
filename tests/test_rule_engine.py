import pytest

from centaurus.evidence.evidence import Evidence
from centaurus.evidence.evidence_source import EvidenceSource
from centaurus.finding.finding import Finding
from centaurus.rules.rule import Rule
from centaurus.rules.rule_engine import RuleEngine


def create_rule() -> Rule:
    """
    Create a valid Rule for testing.
    """

    return Rule(
        name="test-rule",
        description="Test rule",
    )


def create_evidence() -> Evidence:
    """
    Create valid Evidence for testing.
    """

    from datetime import datetime

    return Evidence(
        source=EvidenceSource.WHOIS,
        data={
            "domain_name": "example.org",
        },
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


def test_rule_engine_requires_a_rule() -> None:
    """
    RuleEngine evaluates a Rule.
    """

    engine = RuleEngine()

    evidence = create_evidence()

    with pytest.raises((TypeError, ValueError)):
        engine.evaluate(
            rule=None,
            evidence=evidence,
        )


def test_rule_engine_requires_evidence() -> None:
    """
    RuleEngine evaluates Evidence.
    """

    engine = RuleEngine()

    rule = create_rule()

    with pytest.raises((TypeError, ValueError)):
        engine.evaluate(
            rule=rule,
            evidence=None,
        )


def test_rule_engine_rejects_invalid_rule() -> None:
    """
    RuleEngine rejects objects that are not Rule instances.
    """

    engine = RuleEngine()

    evidence = create_evidence()

    with pytest.raises(TypeError):
        engine.evaluate(
            rule="not a rule",
            evidence=evidence,
        )


def test_rule_engine_rejects_invalid_evidence() -> None:
    """
    RuleEngine rejects objects that are not Evidence instances.
    """

    engine = RuleEngine()

    rule = create_rule()

    with pytest.raises(TypeError):
        engine.evaluate(
            rule=rule,
            evidence="not evidence",
        )


def test_rule_engine_returns_finding() -> None:
    """
    RuleEngine returns a Finding when a Rule is evaluated
    against Evidence.
    """

    engine = RuleEngine()

    rule = create_rule()
    evidence = create_evidence()

    finding = engine.evaluate(
        rule=rule,
        evidence=evidence,
    )

    assert isinstance(
        finding,
        Finding,
    )


def test_finding_is_associated_with_rule() -> None:
    """
    The resulting Finding references the evaluated Rule.
    """

    engine = RuleEngine()

    rule = create_rule()
    evidence = create_evidence()

    finding = engine.evaluate(
        rule=rule,
        evidence=evidence,
    )

    assert finding.rule is rule


def test_finding_is_supported_by_evidence() -> None:
    """
    The resulting Finding references the supporting Evidence.
    """

    engine = RuleEngine()

    rule = create_rule()
    evidence = create_evidence()

    finding = engine.evaluate(
        rule=rule,
        evidence=evidence,
    )

    assert evidence in finding.evidence