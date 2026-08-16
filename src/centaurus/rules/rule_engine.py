"""
Rule Engine component.
"""

from datetime import datetime, timedelta
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
                condition.field in evidence.data
                and value is None
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

        if operator in {
            "age_less_than",
            "expires_within",
            "expired",
        }:
            return self._temporal_condition_matches(
                operator=operator,
                condition=condition,
                evidence=evidence,
                value=value,
            )

        raise ValueError(
            f"Unsupported Rule operator: {operator!r}"
        )

    def _temporal_condition_matches(
        self,
        operator: str,
        condition: Condition,
        evidence: Evidence,
        value: Any,
    ) -> bool:
        """
        Evaluate the minimal temporal operators required by the project.

        Temporal comparisons use Evidence.collected_at as the fixed
        reference point. They never use the current system clock.
        """

        reference = evidence.collected_at
        temporal_value = self._parse_datetime(value)

        if temporal_value is None:
            return False

        if reference.tzinfo is None and temporal_value.tzinfo is not None:
            temporal_value = temporal_value.replace(tzinfo=None)
        elif reference.tzinfo is not None and temporal_value.tzinfo is None:
            temporal_value = temporal_value.replace(tzinfo=reference.tzinfo)

        if operator == "expired":
            return temporal_value < reference

        if not isinstance(condition.value, (int, float)) or isinstance(
            condition.value, bool
        ):
            raise TypeError(
                f"Temporal Rule operator {operator!r} requires a numeric day value."
            )

        if condition.value < 0:
            raise ValueError(
                f"Temporal Rule operator {operator!r} requires a non-negative day value."
            )

        delta = timedelta(days=condition.value)

        if operator == "age_less_than":
            age = reference - temporal_value
            return timedelta(0) <= age < delta

        if operator == "expires_within":
            remaining = temporal_value - reference
            return timedelta(0) <= remaining <= delta

        raise ValueError(
            f"Unsupported temporal Rule operator: {operator!r}"
        )

    @staticmethod
    def _parse_datetime(value: Any) -> datetime | None:
        """
        Parse a temporal Evidence value.

        The normalizer remains responsible for preserving observed values.
        The Rule Engine accepts datetime objects and ISO-8601 strings for
        temporal Rule evaluation.
        """

        if isinstance(value, datetime):
            return value

        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return None

        return None

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