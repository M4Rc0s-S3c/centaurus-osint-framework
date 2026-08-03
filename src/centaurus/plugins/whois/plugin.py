"""
WHOIS plugin implementation.
"""

import whois

from centaurus.plugins.base_plugin import BasePlugin


class Plugin(BasePlugin):
    """
    WHOIS plugin.
    """

    def execute(
        self,
        parameters: dict,
    ) -> dict:
        """
        Execute a WHOIS lookup and return the raw result.
        """

        domain = parameters.get(
            "domain",
            "unknown",
        )

        if domain == "unknown":
            return {
                "plugin": "whois",
                "status": "completed",
                "data": {},
            }

        result = whois.whois(domain)

        return {
            "plugin": "whois",
            "status": "completed",
            "data": dict(result),
        }