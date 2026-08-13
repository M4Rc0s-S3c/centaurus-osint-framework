"""
Minimal WHOIS/RDAP rule definitions.

These rules operate on normalized Evidence fields and deliberately contain
no derived temporal semantics.
"""

from centaurus.rules.condition import Condition
from centaurus.rules.rule import Rule


RL_001 = Rule(
    id="RL-001",
    version="1.0",
    name="missing_registrar",
    description="Registrar information is missing.",
    category="whois",
    conditions=(
        Condition(field="registrar", operator="missing"),
    ),
    conclusion="WHOIS information does not contain registrar information.",
)

RL_002 = Rule(
    id="RL-002",
    version="1.0",
    name="missing_name_servers",
    description="Name server information is missing.",
    category="whois",
    conditions=(
        Condition(field="name_servers", operator="missing"),
    ),
    conclusion="WHOIS information does not contain name server information.",
)


WHOIS_RULES = (RL_001, RL_002)

__all__ = ["RL_001", "RL_002", "WHOIS_RULES"]
