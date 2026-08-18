"""
WHOIS plugin implementation.
"""

from datetime import datetime, timezone

import whois

from centaurus.evidence import EvidenceSource, RawObservation
from centaurus.plugins.base_plugin import BasePlugin


_WHOIS_TIMEOUT_SECONDS = 10


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
            result = whois.whois(
                domain,
                timeout=_WHOIS_TIMEOUT_SECONDS,
                ignore_socket_errors=False,
            )
            data = dict(result)

        collected_at = datetime.now(timezone.utc)

        return RawObservation(
            source=EvidenceSource.WHOIS,
            data=data,
            collected_at=collected_at,
        )