"""Minimal DNS rule definitions."""

from centaurus.rules.condition import Condition
from centaurus.rules.rule import Rule


RL_007_SPF_POLICY_NOT_OBSERVED = Rule(
    id="RL-007",
    version="1.0",
    name="spf_policy_not_observed",
    description="An SPF policy was not observed in the normalized DNS evidence.",
    category="dns",
    conditions=(
        Condition(
            field="spf_records",
            operator="equals",
            value=[],
        ),
    ),
    conclusion="No SPF policy was observed in the normalized DNS evidence.",
)

DNS_RULES = (
    RL_007_SPF_POLICY_NOT_OBSERVED,
)
