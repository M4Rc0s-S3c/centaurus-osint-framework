"""Product Rule catalog used by the distribution composition root."""

from centaurus.rules.dns_rules import DNS_RULES
from centaurus.rules.exposure_rules import EXPOSURE_RULES
from centaurus.rules.whois_rules import WHOIS_RULES


_ALL_RULES = WHOIS_RULES + DNS_RULES + EXPOSURE_RULES
DEFAULT_RULES = tuple(
    sorted(_ALL_RULES, key=lambda rule: int(rule.id.removeprefix("RL-")))
)


__all__ = ["DEFAULT_RULES"]
