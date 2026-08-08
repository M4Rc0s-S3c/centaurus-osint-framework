"""
Tests for the Rule domain value object.
"""

from dataclasses import FrozenInstanceError

import pytest

from centaurus.rules.condition import Condition
from centaurus.rules.rule import Rule


def create_condition() -> Condition:
    """
    Create a valid Condition for testing.
    """

    return Condition(
        field="domain_age_days",
        operator="less_than",
        value=30,
    )


def create_rule() -> Rule:
    """
    Create a valid Rule for testing.
    """

    return Rule(
        id="RL-001",
        version="1.0",
        name="young-domain",
        description="Domain is very recent.",
        category="whois_rdap",
        conditions=(
            create_condition(),
        ),
        conclusion="Domain is younger than 30 days.",
    )


def test_rule_can_be_created() -> None:
    """
    A Rule can be instantiated.
    """

    rule = create_rule()

    assert isinstance(
        rule,
        Rule,
    )


def test_rule_stores_id() -> None:
    """
    Rule stores its identifier.
    """

    rule = create_rule()

    assert rule.id == "RL-001"


def test_rule_stores_version() -> None:
    """
    Rule stores its version.
    """

    rule = create_rule()

    assert rule.version == "1.0"


def test_rule_stores_name() -> None:
    """
    Rule stores its name.
    """

    rule = create_rule()

    assert rule.name == "young-domain"


def test_rule_stores_description() -> None:
    """
    Rule stores its description.
    """

    rule = create_rule()

    assert rule.description == (
        "Domain is very recent."
    )


def test_rule_stores_category() -> None:
    """
    Rule stores its analysis category.
    """

    rule = create_rule()

    assert rule.category == "whois_rdap"


def test_rule_stores_conditions() -> None:
    """
    Rule stores its Conditions.
    """

    condition = create_condition()

    rule = Rule(
        id="RL-001",
        version="1.0",
        name="young-domain",
        description="Domain is very recent.",
        category="whois_rdap",
        conditions=(condition,),
        conclusion="Domain is younger than 30 days.",
    )

    assert rule.conditions == (
        condition,
    )


def test_rule_conditions_are_a_tuple() -> None:
    """
    Rule exposes Conditions as an immutable collection.
    """

    rule = create_rule()

    assert isinstance(
        rule.conditions,
        tuple,
    )


def test_rule_stores_conclusion() -> None:
    """
    Rule stores the conclusion associated with
    a matching condition.
    """

    rule = create_rule()

    assert rule.conclusion == (
        "Domain is younger than 30 days."
    )


def test_rule_is_immutable() -> None:
    """
    Rule is immutable.
    """

    rule = create_rule()

    with pytest.raises(FrozenInstanceError):
        rule.name = "modified-rule"  # type: ignore[misc]


def test_rule_has_no_evaluation_responsibility() -> None:
    """
    Rule does not evaluate Evidence by itself.

    Evaluation remains the responsibility of RuleEngine.
    """

    rule = create_rule()

    assert not hasattr(
        rule,
        "evaluate",
    )