"""
WHOIS plugin implementation.
"""

from datetime import datetime, timezone

import whois

from centaurus.evidence import EvidenceSource, RawObservation
from centaurus.plugins.base_plugin import BasePlugin


class Plugin(BasePlugin):
    """
    WHOIS plugin.
    """

    def execute(
        self,
        parameters: dict,
    ) -> RawObservation:
        """
        Execute a WHOIS lookup and return the raw observation.
        """

        collected_at = datetime.now(timezone.utc)

        domain = parameters.get(
            "domain",
            "unknown",
        )

        if domain == "unknown":
            data = {}
        else:
            result = whois.whois(domain)
            data = dict(result)

        collected_at = datetime.now(timezone.utc)

        return RawObservation(
            source=EvidenceSource.WHOIS,
            data=data,
            collected_at=collected_at,
        )