"""
Minimal WHOIS/RDAP rule definitions.
"""

from centaurus.rules.condition import Condition
from centaurus.rules.rule import Rule


RL_001_MISSING_REGISTRAR = Rule(
    id="RL-001",
    version="1.0",
    name="missing_registrar",
    description="Registrar information is missing.",
    category="whois",
    conditions=(Condition(field="registrar", operator="missing"),),
    conclusion="WHOIS information does not contain registrar information.",
)

RL_002_MISSING_NAME_SERVERS = Rule(
    id="RL-002",
    version="1.0",
    name="missing_name_servers",
    description="Name server information is missing.",
    category="whois",
    conditions=(Condition(field="name_servers", operator="missing"),),
    conclusion="WHOIS information does not contain name server information.",
)

RL_003_INCOMPLETE_REGISTRATION_INFORMATION = Rule(
    id="RL-003",
    version="1.0",
    name="incomplete_registration_information",
    description="Relevant registration information is missing.",
    category="whois",
    conditions=(
        Condition(field="creation_date", operator="missing"),
        Condition(field="expiration_date", operator="missing"),
    ),
    conclusion="Registration information is missing: {field}.",
)

RL_004_DNSSEC_STATUS_OBSERVED = Rule(
    id="RL-004",
    version="1.0",
    name="dnssec_status_observed",
    description="DNSSEC status is reported by the WHOIS evidence.",
    category="whois",
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
    conclusion="DNSSEC status is reported in the WHOIS evidence.",
)


RL_005_REGISTRANT_NAME_UNAVAILABLE = Rule(
    id="RL-005",
    version="1.0",
    name="registrant_name_unavailable",
    description="Registrant name information is missing or explicitly redacted.",
    category="whois",
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
    conclusion="Registrant name information is unavailable.",
)

WHOIS_RULES = (
    RL_001_MISSING_REGISTRAR,
    RL_002_MISSING_NAME_SERVERS,
    RL_003_INCOMPLETE_REGISTRATION_INFORMATION,
    RL_004_DNSSEC_STATUS_OBSERVED,
    RL_005_REGISTRANT_NAME_UNAVAILABLE,
)
