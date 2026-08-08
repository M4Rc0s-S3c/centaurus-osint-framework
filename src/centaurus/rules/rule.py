"""
Rule domain value object.
"""

from dataclasses import dataclass

from centaurus.rules.condition import Condition


@dataclass(frozen=True, slots=True)
class Rule:
    """
    Immutable Value Object representing a declarative
    domain evaluation criterion.
    """

    id: str
    version: str
    name: str
    description: str
    category: str
    conditions: tuple[Condition, ...]
    conclusion: str