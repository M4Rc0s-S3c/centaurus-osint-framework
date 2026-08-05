from dataclasses import FrozenInstanceError

import pytest

from centaurus.rules.rule import Rule


def test_rule_can_be_created() -> None:
    """
    A Rule can be instantiated.
    """

    rule = Rule(
        name="example-rule",
        description="Example evaluation criterion.",
    )

    assert isinstance(
        rule,
        Rule,
    )


def test_rule_stores_name() -> None:
    """
    Rule stores its name.
    """

    name = "example-rule"

    rule = Rule(
        name=name,
        description="Example evaluation criterion.",
    )

    assert rule.name == name


def test_rule_stores_description() -> None:
    """
    Rule stores its description.
    """

    description = "Example evaluation criterion."

    rule = Rule(
        name="example-rule",
        description=description,
    )

    assert rule.description == description


def test_rule_is_immutable() -> None:
    """
    Rule is immutable.
    """

    rule = Rule(
        name="example-rule",
        description="Example evaluation criterion.",
    )

    with pytest.raises(FrozenInstanceError):
        rule.name = "modified-rule"  # type: ignore[misc]


def test_rule_has_no_evaluation_responsibility() -> None:
    """
    Rule does not evaluate Evidence by itself.

    Evaluation remains the responsibility of RuleEngine.
    """

    rule = Rule(
        name="example-rule",
        description="Example evaluation criterion.",
    )

    assert not hasattr(
        rule,
        "evaluate",
    )

def evaluator(evidence: Evidence) -> str | None:
    if evidence.data.get("domain_name") == "example.org":
        return "Domain matches example.org"

    return None
