"""
Finding Value Object.

Represents a conclusion produced by applying a Rule to Evidence.
"""

from dataclasses import dataclass
from typing import Any

from centaurus.evidence.evidence import Evidence
from centaurus.rules.rule import Rule


@dataclass(frozen=True, slots=True)
class Finding:
    """
    Immutable Value Object representing a finding.

    A Finding contains:

    - the conclusion produced by a Rule;
    - the Rule responsible for the conclusion;
    - the Evidence supporting the conclusion.

    Finding does not evaluate Evidence and does not contain
    investigation logic.
    """

    conclusion: str
    rule: Rule
    evidences: tuple[Evidence, ...]