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
    ) -> None:
        """
        Execute the WHOIS plugin.

        The actual WHOIS query will be implemented in a future
        runtime milestone.
        """

        print(
            "Executing WHOIS plugin",
            parameters,
        )
