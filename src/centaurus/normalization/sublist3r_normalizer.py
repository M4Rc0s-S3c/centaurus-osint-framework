"""Deterministic normalization of Sublist3r RAW results."""

from typing import Any


def normalize_sublist3r_data(
    data: dict[str, Any],
) -> dict[str, Any]:
    """Normalize Sublist3r hostnames into a stable Evidence vocabulary.

    The transformation canonicalizes textual hostnames and removes duplicate
    representation. It does not infer ownership, exposure or risk.
    """

    domain = data.get("domain")
    if isinstance(domain, str) and domain.strip():
        domain_name = domain.strip().rstrip(".").lower()
    else:
        domain_name = None

    raw_subdomains = data.get("subdomains")
    if not isinstance(raw_subdomains, list):
        raw_subdomains = []

    normalized_subdomains: list[str] = []
    seen: set[str] = set()

    for value in raw_subdomains:
        if not isinstance(value, str):
            continue

        hostname = value.strip().rstrip(".").lower()
        if not hostname or hostname in seen:
            continue

        seen.add(hostname)
        normalized_subdomains.append(hostname)

    normalized_subdomains.sort()

    return {
        "domain_name": domain_name,
        "subdomains": normalized_subdomains,
    }
