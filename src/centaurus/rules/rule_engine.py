"""
Rule Engine component.
"""

from centaurus.evidence.evidence import Evidence
from centaurus.finding.finding import Finding
from centaurus.rules.rule import Rule


class RuleEngine:
    """
    Rule Engine component.

    Responsible for evaluating a Rule against Evidence
    and producing a Finding.
    """

    def evaluate(
        self,
        rule: Rule,
        evidence: Evidence,
    ) -> Finding:
        """
        Evaluate one Rule against one Evidence.

        The semantic evaluation logic is intentionally minimal
        at this stage. The method establishes the application
        contract between Rule, Evidence, and Finding.
        """

        if not isinstance(rule, Rule):
            raise TypeError(
                "Expected a Rule instance."
            )

        if not isinstance(evidence, Evidence):
            raise TypeError(
                "Expected an Evidence instance."
            )

        return Finding(
            rule=rule,
            evidences=(evidence,),
            conclusion=(
                f"Rule '{rule.name}' evaluated against "
                f"the provided Evidence."
            ),
        )