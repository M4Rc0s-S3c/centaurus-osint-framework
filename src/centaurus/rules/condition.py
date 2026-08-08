"""
Rule condition value object.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Condition:
    """
    Immutable Value Object representing one declarative Rule condition.

    A Condition identifies:

    - the Evidence field to inspect;
    - the operator to apply;
    - the value used by the operator, when required.

    Condition does not evaluate Evidence by itself.
    """

    field: str
    operator: str
    value: Any = None