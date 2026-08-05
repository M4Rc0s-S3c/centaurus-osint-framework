"""
Rule domain value object.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Rule:
    """
    Immutable Value Object representing a domain evaluation criterion.
    """

    name: str
    description: str