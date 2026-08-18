"""RDAP plugin implementation."""

from datetime import datetime, timezone
import ipaddress
from urllib.parse import quote

import httpx

from centaurus.config import tool_timeout
from centaurus.evidence import EvidenceSource, RawObservation
from centaurus.plugins.base_plugin import BasePlugin


_DNS_BOOTSTRAP_URL = "https://data.iana.org/rdap/dns.json"
_IPV4_BOOTSTRAP_URL = "https://data.iana.org/rdap/ipv4.json"
_IPV6_BOOTSTRAP_URL = "https://data.iana.org/rdap/ipv6.json"
_RDAP_HEADERS = {
    "Accept": "application/rdap+json",
    "User-Agent": "centaurus/0.4",
}
class Plugin(BasePlugin):
    """RDAP lookup plugin for domain names and IP addresses."""

    def __init__(self, timeout: float | None = None) -> None:
        self._timeout = tool_timeout("rdap", timeout)

    def execute(
        self,
        parameters: dict,
    ) -> RawObservation:
        """Execute one RDAP lookup and return the original JSON response."""

        domain = parameters.get("domain")
        address = parameters.get("ip")

        if domain and address:
            raise ValueError("RDAP task must contain either 'domain' or 'ip', not both.")

        if domain:
            data = self._lookup_domain(str(domain))
        elif address:
            data = self._lookup_ip(str(address))
        else:
            data = {}

        return RawObservation(
            source=EvidenceSource.RDAP,
            data=data,
            collected_at=datetime.now(timezone.utc),
        )

    def _lookup_domain(self, domain: str) -> dict:
        """Resolve the authoritative RDAP service and query one domain."""

        normalized = domain.rstrip(".").lower()
        if "." not in normalized:
            raise ValueError("RDAP domain lookup requires a fully qualified domain name.")

        bootstrap = self._get_json(_DNS_BOOTSTRAP_URL)
        tld = normalized.rsplit(".", 1)[-1]
        base_url = self._domain_base_url(bootstrap, tld)
        url = f"{base_url.rstrip('/')}/domain/{quote(normalized, safe='')}"

        return self._get_json(url)

    def _lookup_ip(self, address: str) -> dict:
        """Resolve the authoritative RDAP service and query one IP address."""

        parsed = ipaddress.ip_address(address)
        bootstrap_url = (
            _IPV4_BOOTSTRAP_URL
            if parsed.version == 4
            else _IPV6_BOOTSTRAP_URL
        )
        bootstrap = self._get_json(bootstrap_url)
        base_url = self._ip_base_url(bootstrap, parsed)
        url = f"{base_url.rstrip('/')}/ip/{quote(str(parsed), safe=':')}"

        return self._get_json(url)

    @staticmethod
    def _domain_base_url(bootstrap: dict, tld: str) -> str:
        """Return the RDAP base URL registered for a top-level domain."""

        for service in bootstrap.get("services", []):
            if not isinstance(service, list) or len(service) != 2:
                continue
            scopes, urls = service
            if tld in {str(scope).lower() for scope in scopes} and urls:
                return str(urls[0])

        raise ValueError(f"No RDAP service registered for TLD: {tld}")

    @staticmethod
    def _ip_base_url(
        bootstrap: dict,
        address: ipaddress.IPv4Address | ipaddress.IPv6Address,
    ) -> str:
        """Return the most-specific RDAP service registered for an IP address."""

        matches: list[tuple[int, str]] = []

        for service in bootstrap.get("services", []):
            if not isinstance(service, list) or len(service) != 2:
                continue
            scopes, urls = service
            if not urls:
                continue

            for scope in scopes:
                try:
                    network = ipaddress.ip_network(str(scope), strict=False)
                except ValueError:
                    continue

                if network.version == address.version and address in network:
                    matches.append((network.prefixlen, str(urls[0])))

        if not matches:
            raise ValueError(f"No RDAP service registered for IP address: {address}")

        return max(matches, key=lambda item: item[0])[1]

    def _get_json(self, url: str) -> dict:
        """Fetch one JSON document without retaining network resources."""

        response = httpx.get(
            url,
            headers=_RDAP_HEADERS,
            timeout=self._timeout,
            follow_redirects=True,
        )
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, dict):
            raise ValueError("RDAP response must be a JSON object.")

        return data
