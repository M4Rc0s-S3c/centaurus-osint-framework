"""
Rule Engine component.
"""

from typing import Any

from centaurus.evidence.evidence import Evidence
from centaurus.finding.finding import Finding
from centaurus.rules.condition import Condition
from centaurus.rules.rule import Rule


class RuleEngine:
    """
    Rule Engine component.

    Responsible for evaluating declarative Rules against
    normalized Evidence and producing zero or more Findings.

    The Rule Engine does not own Rules or Evidence.
    It does not orchestrate the Investigation lifecycle.
    """

    def evaluate(
        self,
        rules: tuple[Rule, ...],
        evidences: tuple[Evidence, ...],
    ) -> tuple[Finding, ...]:
        """
        Evaluate Rules against Evidence.

        A completed evaluation always returns a collection
        of Findings. The collection may contain zero, one,
        or multiple Findings.

        Parameters
        ----------
        rules:
            Rules to evaluate.

        evidences:
            Normalized Evidence available to the evaluation.

        Returns
        -------
        tuple[Finding, ...]
            Findings produced by the evaluation.

        Raises
        ------
        TypeError
            If rules or evidences contain invalid objects.
        """

        if not isinstance(rules, tuple):
            raise TypeError(
                "Expected rules to be a tuple of Rule instances."
            )

        if not isinstance(evidences, tuple):
            raise TypeError(
                "Expected evidences to be a tuple of Evidence instances."
            )

        for rule in rules:
            if not isinstance(rule, Rule):
                raise TypeError(
                    "Expected all rules to be Rule instances."
                )

        for evidence in evidences:
            if not isinstance(evidence, Evidence):
                raise TypeError(
                    "Expected all evidences to be Evidence instances."
                )

        findings: list[Finding] = []

        for rule in rules:
            findings.extend(
                self._evaluate_rule(
                    rule=rule,
                    evidences=evidences,
                )
            )

        return tuple(findings)

    def _evaluate_rule(
        self,
        rule: Rule,
        evidences: tuple[Evidence, ...],
    ) -> tuple[Finding, ...]:
        """
        Evaluate one Rule against the available Evidence.

        A Rule may produce zero or multiple Findings.
        """

        findings: list[Finding] = []

        for condition in rule.conditions:
            for evidence in evidences:

                if self._condition_matches(
                    condition=condition,
                    evidence=evidence,
                ):
                    findings.append(
                        Finding(
                            conclusion=self._build_conclusion(
                                rule=rule,
                                condition=condition,
                            ),
                            rule=rule,
                            evidences=(evidence,),
                        )
                    )

        return tuple(findings)

    def _condition_matches(
        self,
        condition: Condition,
        evidence: Evidence,
    ) -> bool:
        """
        Evaluate one Condition against one Evidence.

        Only the minimal operator set required by the
        current WHOIS/RDAP Rules is supported.
        """

        if condition.field not in evidence.data:
            value = None
        else:
            value = evidence.data[condition.field]

        operator = condition.operator

        if operator == "missing":
            return (
                condition.field not in evidence.data
                or value is None
            )

        if operator == "redacted":
            return value == "[REDACTED]"

        if operator == "equals":
            return value == condition.value

        if operator == "less_than":
            return value < condition.value

        if operator == "greater_than":
            return value > condition.value

        if operator == "less_than_or_equal":
            return value <= condition.value

        if operator == "greater_than_or_equal":
            return value >= condition.value

        raise ValueError(
            f"Unsupported Rule operator: {operator!r}"
        )

    def _build_conclusion(
        self,
        rule: Rule,
        condition: Condition,
    ) -> str:
        """
        Build the Finding conclusion from the Rule definition.

        The current implementation keeps conclusion generation
        deliberately simple. Template expansion can be added
        when the declarative Rule definitions require it.
        """

        if "{field}" in rule.conclusion:
            return rule.conclusion.format(
                field=condition.field,
            )

        return rule.conclusion