"""Deterministic normalization of crt.sh Certificate Transparency results."""

from typing import Any


def normalize_crtsh_data(
    data: dict[str, Any],
) -> dict[str, Any]:
    """Normalize crt.sh rows into a stable Certificate Transparency vocabulary.

    The transformation stabilizes certificate-row field names and DNS-name
    representation. It does not infer ownership, liveness, novelty or risk.
    """

    domain_name = _normalize_domain(data.get("domain"))
    raw_certificates = data.get("certificates")
    if not isinstance(raw_certificates, list):
        raw_certificates = []

    certificates: list[dict[str, Any]] = []
    certificate_names: set[str] = set()
    subdomains: set[str] = set()

    for raw_certificate in raw_certificates:
        if not isinstance(raw_certificate, dict):
            continue

        names = _certificate_names(raw_certificate)
        certificate_names.update(names)

        if domain_name is not None:
            for name in names:
                candidate = name[2:] if name.startswith("*.") else name
                if candidate != domain_name and candidate.endswith(f".{domain_name}"):
                    subdomains.add(candidate)

        certificate_id = raw_certificate.get("id")
        if certificate_id is None:
            certificate_id = raw_certificate.get("min_cert_id")

        entry_timestamp = raw_certificate.get("entry_timestamp")
        if entry_timestamp is None:
            entry_timestamp = raw_certificate.get("min_entry_timestamp")

        certificates.append(
            {
                "issuer_ca_id": raw_certificate.get("issuer_ca_id"),
                "issuer_name": raw_certificate.get("issuer_name"),
                "common_name": _normalize_dns_name(raw_certificate.get("common_name")),
                "names": names,
                "certificate_id": certificate_id,
                "entry_timestamp": entry_timestamp,
                "not_before": raw_certificate.get("not_before"),
                "not_after": raw_certificate.get("not_after"),
                "serial_number": raw_certificate.get("serial_number"),
            }
        )

    return {
        "domain_name": domain_name,
        "certificates": certificates,
        "certificate_names": sorted(certificate_names),
        "subdomains": sorted(subdomains),
    }


def _normalize_domain(value: Any) -> str | None:
    if not isinstance(value, str):
        return None

    normalized = value.strip().rstrip(".").lower()
    return normalized or None


def _normalize_dns_name(value: Any) -> str | None:
    if not isinstance(value, str):
        return None

    normalized = value.strip().rstrip(".").lower()
    return normalized or None


def _certificate_names(record: dict[str, Any]) -> list[str]:
    values: list[str] = []

    common_name = _normalize_dns_name(record.get("common_name"))
    if common_name is not None:
        values.append(common_name)

    name_value = record.get("name_value")
    if isinstance(name_value, str):
        for line in name_value.splitlines():
            normalized = _normalize_dns_name(line)
            if normalized is not None:
                values.append(normalized)

    return sorted(set(values))
