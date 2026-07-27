"""
WHOIS plugin implementation.
"""

from centaurus.plugins.base_plugin import BasePlugin


class Plugin(BasePlugin):
    """
    WHOIS plugin.
    """

    def execute(self) -> None:
        """
        Execute the WHOIS plugin.
        """

        #
        # Temporary implementation.
        # Future versions will perform the actual WHOIS query.
        #

        print("Executing WHOIS plugin")
