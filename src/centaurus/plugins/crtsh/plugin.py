"""crt.sh Certificate Transparency lookup plugin implementation."""

from datetime import datetime, timezone

import httpx

from centaurus.evidence import EvidenceSource, RawObservation
from centaurus.plugins.base_plugin import BasePlugin


_CRTSH_URL = "https://crt.sh/"
_CRTSH_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "centaurus/0.4",
}
_CRTSH_TIMEOUT_SECONDS = 30.0


class Plugin(BasePlugin):
    """Passive crt.sh Certificate Transparency lookup for domain targets."""

    def execute(
        self,
        parameters: dict,
    ) -> RawObservation:
        """Query crt.sh and return the original JSON certificate rows."""

        domain = str(parameters.get("domain", "")).strip().rstrip(".").lower()

        if not domain:
            data = {}
        else:
            data = self._lookup_domain(domain)

        return RawObservation(
            source=EvidenceSource.CRTSH,
            data=data,
            collected_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def _lookup_domain(domain: str) -> dict:
        """Query the crt.sh JSON interface for certificates below one domain."""

        response = httpx.get(
            _CRTSH_URL,
            params={
                "q": f"%.{domain}",
                "output": "json",
            },
            headers=_CRTSH_HEADERS,
            timeout=_CRTSH_TIMEOUT_SECONDS,
            follow_redirects=True,
        )
        response.raise_for_status()

        try:
            records = response.json()
        except ValueError as exc:
            raise RuntimeError("crt.sh produced an invalid JSON response.") from exc

        if not isinstance(records, list) or not all(
            isinstance(record, dict) for record in records
        ):
            raise ValueError("crt.sh response must be a JSON array of objects.")

        return {
            "domain": domain,
            "certificates": records,
        }
