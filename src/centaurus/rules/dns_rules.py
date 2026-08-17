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

RL_010_DIRECT_DMARC_POLICY_NOT_OBSERVED = Rule(
    id="RL-010",
    version="1.0",
    name="direct_dmarc_policy_not_observed",
    description=(
        "A direct DMARC policy record was not observed at the target domain's "
        "_dmarc DNS name."
    ),
    category="dns",
    conditions=(
        Condition(
            field="dmarc_records",
            operator="equals",
            value=[],
        ),
    ),
    conclusion=(
        "No direct DMARC policy record was observed at the target domain's "
        "_dmarc DNS name."
    ),
)

DNS_RULES = (
    RL_007_SPF_POLICY_NOT_OBSERVED,
    RL_010_DIRECT_DMARC_POLICY_NOT_OBSERVED,
)
