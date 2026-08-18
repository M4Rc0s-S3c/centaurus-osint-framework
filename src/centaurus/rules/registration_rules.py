"""Declarative registration rules over normalized Evidence."""

from centaurus.rules.condition import Condition
from centaurus.rules.rule import Rule


RL_001_MISSING_REGISTRAR = Rule(
    id="RL-001",
    version="1.1",
    name="missing_registrar",
    description=(
        "Registrar information was not observed in normalized registration "
        "Evidence."
    ),
    category="registration",
    conditions=(Condition(field="registrar", operator="missing"),),
    conclusion=(
        "Registrar information was not observed in normalized registration "
        "Evidence."
    ),
)

RL_002_MISSING_NAME_SERVERS = Rule(
    id="RL-002",
    version="1.1",
    name="missing_name_servers",
    description=(
        "Name server information was not observed in normalized registration "
        "Evidence."
    ),
    category="registration",
    conditions=(Condition(field="name_servers", operator="missing"),),
    conclusion=(
        "Name server information was not observed in normalized registration "
        "Evidence."
    ),
)

RL_003_INCOMPLETE_REGISTRATION_INFORMATION = Rule(
    id="RL-003",
    version="1.1",
    name="incomplete_registration_information",
    description=(
        "A relevant registration field was not observed in normalized "
        "registration Evidence."
    ),
    category="registration",
    conditions=(
        Condition(field="creation_date", operator="missing"),
        Condition(field="expiration_date", operator="missing"),
    ),
    conclusion=(
        "Registration field was not observed in normalized registration "
        "Evidence: {field}."
    ),
)

RL_004_DNSSEC_STATUS_OBSERVED = Rule(
    id="RL-004",
    version="1.1",
    name="dnssec_status_observed",
    description=(
        "A recognized DNSSEC status was observed in normalized registration "
        "Evidence."
    ),
    category="registration",
    conditions=(
        Condition(
            field="dnssec",
            operator="equals",
            value="signedDelegation",
        ),
        Condition(
            field="dnssec",
            operator="equals",
            value="unsigned",
        ),
    ),
    conclusion=(
        "A recognized DNSSEC status was observed in normalized registration "
        "Evidence."
    ),
)


RL_005_REGISTRANT_NAME_UNAVAILABLE = Rule(
    id="RL-005",
    version="1.1",
    name="registrant_name_unavailable",
    description=(
        "Registrant name information was not observed or was explicitly "
        "redacted in normalized registration Evidence."
    ),
    category="registration",
    conditions=(
        Condition(
            field="registrant_name",
            operator="missing",
        ),
        Condition(
            field="registrant_name",
            operator="redacted",
            value="[REDACTED]",
        ),
    ),
    conclusion=(
        "Registrant name information was not available in normalized "
        "registration Evidence."
    ),
)


RL_006_DOMAIN_CREATED_RECENTLY = Rule(
    id="RL-006",
    version="1.1",
    name="domain_created_recently",
    description=(
        "Reports when a domain was created less than 30 days before Evidence "
        "collection."
    ),
    category="registration",
    conditions=(
        Condition(
            field="creation_date",
            operator="age_less_than",
            value=30,
        ),
    ),
    conclusion="Domain was created less than 30 days before collection.",
)

REGISTRATION_RULES = (
    RL_001_MISSING_REGISTRAR,
    RL_002_MISSING_NAME_SERVERS,
    RL_003_INCOMPLETE_REGISTRATION_INFORMATION,
    RL_004_DNSSEC_STATUS_OBSERVED,
    RL_005_REGISTRANT_NAME_UNAVAILABLE,
    RL_006_DOMAIN_CREATED_RECENTLY,
)
