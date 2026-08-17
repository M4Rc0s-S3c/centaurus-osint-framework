"""Declarative public-exposure rules over normalized collections."""

from centaurus.rules.condition import Condition
from centaurus.rules.rule import Rule


RL_008_MULTIPLE_PUBLIC_SUBDOMAINS_OBSERVED = Rule(
    id="RL-008",
    version="1.0",
    name="multiple_public_subdomains_observed",
    description=(
        "Reports when normalized Evidence contains more than one public subdomain."
    ),
    category="public_exposure",
    conditions=(
        Condition(
            field="subdomains",
            operator="collection_size_greater_than",
            value=1,
        ),
    ),
    conclusion="Multiple public subdomains were observed in normalized Evidence.",
)


RL_009_MULTIPLE_PUBLIC_EMAILS_OBSERVED = Rule(
    id="RL-009",
    version="1.0",
    name="multiple_public_emails_observed",
    description=(
        "Reports when normalized Evidence contains more than one public email address."
    ),
    category="public_exposure",
    conditions=(
        Condition(
            field="emails",
            operator="collection_size_greater_than",
            value=1,
        ),
    ),
    conclusion=(
        "Multiple public email addresses were observed in normalized Evidence."
    ),
)


EXPOSURE_RULES = (
    RL_008_MULTIPLE_PUBLIC_SUBDOMAINS_OBSERVED,
    RL_009_MULTIPLE_PUBLIC_EMAILS_OBSERVED,
)
