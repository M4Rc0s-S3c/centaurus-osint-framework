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
            if condition.operator == "shared_collection_item_min_sources":
                findings.extend(
                    self._evaluate_shared_collection_item_condition(
                        rule=rule,
                        condition=condition,
                        evidences=evidences,
                    )
                )
                continue

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

    def _evaluate_shared_collection_item_condition(
        self,
        rule: Rule,
        condition: Condition,
        evidences: tuple[Evidence, ...],
    ) -> tuple[Finding, ...]:
        """Correlate collection items across distinct Evidence sources.

        One normalized string item matches only when it appears in at least
        ``Condition.value`` distinct EvidenceSource values. Repeated Evidence
        from the same source cannot satisfy the source threshold by itself.
        One Finding is produced per corroborated item and keeps the first
        supporting Evidence from every distinct source in evaluation order.
        """

        minimum_sources = condition.value

        if not isinstance(minimum_sources, int) or isinstance(
            minimum_sources, bool
        ):
            raise TypeError(
                "Rule operator 'shared_collection_item_min_sources' "
                "requires an integer source threshold."
            )

        if minimum_sources < 2:
            raise ValueError(
                "Rule operator 'shared_collection_item_min_sources' "
                "requires a source threshold of at least 2."
            )

        supporting_evidences: dict[str, list[Evidence]] = {}
        supporting_sources: dict[str, set[Any]] = {}

        for evidence in evidences:
            values = evidence.data.get(condition.field)
            if not isinstance(values, (list, tuple, set, frozenset)):
                continue

            seen_items: set[str] = set()
            for item in values:
                if not isinstance(item, str) or not item or item in seen_items:
                    continue

                seen_items.add(item)
                item_sources = supporting_sources.setdefault(item, set())

                if evidence.source in item_sources:
                    continue

                item_sources.add(evidence.source)
                supporting_evidences.setdefault(item, []).append(evidence)

        findings: list[Finding] = []

        for item in sorted(supporting_evidences):
            if len(supporting_sources[item]) < minimum_sources:
                continue

            findings.append(
                Finding(
                    conclusion=self._build_conclusion(
                        rule=rule,
                        condition=condition,
                        item=item,
                    ),
                    rule=rule,
                    evidences=tuple(supporting_evidences[item]),
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

        The supported operators are generic over normalized Evidence and
        are independent of the tool that produced the observation.
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

        if operator == "collection_size_greater_than":
            return self._collection_size_greater_than(
                condition=condition,
                value=value,
            )

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

    @staticmethod
    def _collection_size_greater_than(
        condition: Condition,
        value: Any,
    ) -> bool:
        """Evaluate collection cardinality against an integer threshold.

        The operator is intentionally limited to concrete collection types
        used by normalized Evidence. Strings and mappings are not treated as
        collections for Rule evaluation.
        """

        threshold = condition.value

        if not isinstance(threshold, int) or isinstance(threshold, bool):
            raise TypeError(
                "Rule operator 'collection_size_greater_than' "
                "requires a non-negative integer value."
            )

        if threshold < 0:
            raise ValueError(
                "Rule operator 'collection_size_greater_than' "
                "requires a non-negative integer value."
            )

        if not isinstance(value, (list, tuple, set, frozenset)):
            return False

        return len(value) > threshold

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
        item: str | None = None,
    ) -> str:
        """Build the deterministic Finding conclusion from a Rule.

        ``{field}`` remains available for field-oriented Rules. ``{item}`` is
        expanded only when multi-Evidence collection correlation identifies
        the concrete normalized item recorded by the Finding.
        """

        conclusion = rule.conclusion.replace(
            "{field}",
            condition.field,
        )

        if item is not None:
            conclusion = conclusion.replace(
                "{item}",
                item,
            )

        return conclusion
