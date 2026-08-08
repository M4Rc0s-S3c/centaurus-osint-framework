"""
Tests for the Rule Condition Value Object.
"""

from dataclasses import FrozenInstanceError

import pytest

from centaurus.rules.condition import Condition


def test_condition_can_be_created() -> None:
    """
    A Condition can be instantiated.
    """

    condition = Condition(
        field="domain_age_days",
        operator="less_than",
        value=30,
    )

    assert isinstance(
        condition,
        Condition,
    )


def test_condition_stores_field() -> None:
    """
    Condition stores the Evidence field to inspect.
    """

    condition = Condition(
        field="domain_age_days",
        operator="less_than",
        value=30,
    )

    assert condition.field == "domain_age_days"


def test_condition_stores_operator() -> None:
    """
    Condition stores its operator.
    """

    condition = Condition(
        field="domain_age_days",
        operator="less_than",
        value=30,
    )

    assert condition.operator == "less_than"


def test_condition_stores_value() -> None:
    """
    Condition stores its comparison value.
    """

    condition = Condition(
        field="domain_age_days",
        operator="less_than",
        value=30,
    )

    assert condition.value == 30


def test_condition_value_is_optional() -> None:
    """
    Conditions such as 'missing' do not require a value.
    """

    condition = Condition(
        field="registrar",
        operator="missing",
    )

    assert condition.value is None


def test_condition_is_immutable() -> None:
    """
    Condition is an immutable Value Object.
    """

    condition = Condition(
        field="domain_age_days",
        operator="less_than",
        value=30,
    )

    with pytest.raises(FrozenInstanceError):
        condition.field = "other_field"  # type: ignore[misc]