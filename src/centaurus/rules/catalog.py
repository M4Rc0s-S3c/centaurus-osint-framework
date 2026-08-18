"""Product Rule catalog used by the distribution composition root."""

from centaurus.rules.dns_rules import DNS_RULES
from centaurus.rules.exposure_rules import EXPOSURE_RULES
from centaurus.rules.registration_rules import REGISTRATION_RULES


_ALL_RULES = REGISTRATION_RULES + DNS_RULES + EXPOSURE_RULES
DEFAULT_RULES = tuple(
    sorted(_ALL_RULES, key=lambda rule: int(rule.id.removeprefix("RL-")))
)


__all__ = ["DEFAULT_RULES"]
