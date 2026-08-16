"""Deterministic normalization of theHarvester JSON reports."""

from ipaddress import ip_address
from typing import Any


def normalize_theharvester_data(
    data: dict[str, Any],
) -> dict[str, Any]:
    """Normalize theHarvester output into a stable passive-OSINT vocabulary.

    The transformation canonicalizes textual representation and derives the
    subdomain inventory from reported hosts. It does not infer ownership,
    liveness, sensitivity, exposure level or risk.
    """

    domain_name = _normalize_hostname(data.get("domain"))
    sources = _normalize_text_list(data.get("sources"), lowercase=True)

    report = data.get("report")
    if not isinstance(report, dict):
        report = {}

    hosts = _normalize_host_list(report.get("hosts"))
    emails = _normalize_text_list(report.get("emails"), lowercase=True)
    ips = _normalize_text_list(report.get("ips"))
    urls = _normalize_text_list(report.get("interesting_urls"))
    asns = _normalize_scalar_list(report.get("asns"))

    subdomains: list[str] = []
    if domain_name is not None:
        subdomains = [
            host
            for host in hosts
            if host != domain_name and host.endswith(f".{domain_name}")
        ]

    return {
        "domain_name": domain_name,
        "sources": sources,
        "hosts": hosts,
        "subdomains": subdomains,
        "emails": emails,
        "ips": ips,
        "urls": urls,
        "asns": asns,
    }


def _normalize_hostname(value: Any) -> str | None:
    if not isinstance(value, str):
        return None

    normalized = value.strip().rstrip(".").lower()
    return normalized or None


def _normalize_host_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []

    normalized: set[str] = set()
    for item in value:
        host = _normalize_reported_host(item)
        if host is not None:
            normalized.add(host)

    return sorted(normalized)


def _normalize_reported_host(value: Any) -> str | None:
    """Normalize a host entry, removing optional theHarvester IP enrichment.

    theHarvester JSON may expose host entries as either a plain hostname or
    ``hostname:address[,address...]``. The addresses are enrichment attached
    to the host representation, not part of the hostname itself.
    """

    host = _normalize_hostname(value)
    if host is None or ":" not in host:
        return host

    candidate, separator, addresses = host.partition(":")
    if not separator or "." not in candidate or not addresses:
        return host

    address_values = [item.strip() for item in addresses.split(",")]
    if not address_values or any(not item for item in address_values):
        return host

    try:
        for address in address_values:
            ip_address(address)
    except ValueError:
        return host

    return _normalize_hostname(candidate)


def _normalize_text_list(
    value: Any,
    *,
    lowercase: bool = False,
) -> list[str]:
    if not isinstance(value, list):
        return []

    normalized: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            continue

        text = item.strip()
        if lowercase:
            text = text.lower()
        if text:
            normalized.add(text)

    return sorted(normalized)


def _normalize_scalar_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []

    normalized: set[str] = set()
    for item in value:
        if isinstance(item, bool) or item is None:
            continue
        if not isinstance(item, (str, int, float)):
            continue

        text = str(item).strip()
        if text:
            normalized.add(text)

    return sorted(normalized)
