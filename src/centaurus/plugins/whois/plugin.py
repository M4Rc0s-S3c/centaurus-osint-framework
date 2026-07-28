"""
WHOIS plugin implementation.
"""

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
        Execute a simulated WHOIS lookup.

        The actual WHOIS query will be implemented in a future
        runtime milestone.
        """

        domain = parameters.get(
            "domain",
            "unknown",
        )

        return {
            "plugin": "whois",
            "status": "completed",
            "data": {
                "domain": domain,
                "registrar": "Example Registrar",
                "creation_date": "1995-08-14",
            },
        }
