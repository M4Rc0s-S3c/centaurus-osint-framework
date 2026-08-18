"""
WHOIS plugin implementation.
"""

from datetime import datetime, timezone

import whois

from centaurus.config import tool_timeout
from centaurus.evidence import EvidenceSource, RawObservation
from centaurus.plugins.base_plugin import BasePlugin


class Plugin(BasePlugin):
    """
    WHOIS plugin.
    """

    def __init__(self, timeout: float | None = None) -> None:
        self._timeout = tool_timeout("whois", timeout)

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
                timeout=self._timeout,
                ignore_socket_errors=False,
            )
            data = dict(result)

        collected_at = datetime.now(timezone.utc)

        return RawObservation(
            source=EvidenceSource.WHOIS,
            data=data,
            collected_at=collected_at,
        )