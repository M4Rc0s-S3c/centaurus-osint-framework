"""Deterministic normalization of DNSRecon RAW records."""

from typing import Any


def normalize_dnsrecon_data(
    data: dict[str, Any],
) -> dict[str, Any]:
    """Normalize DNSRecon records into a stable DNS Evidence vocabulary.

    The transformation groups observed DNS records by their declared record
    type. It does not infer risk, probe additional sources or create findings.
    """

    records = data.get("records")
    if not isinstance(records, list):
        return {
            "domain_name": None,
            "records": [],
            "a_records": [],
            "aaaa_records": [],
            "mx_records": [],
            "ns_records": [],
            "soa_records": [],
            "txt_records": [],
            "spf_records": [],
            "srv_records": [],
            "cname_records": [],
            "scan_info": None,
        }

    normalized_records: list[dict[str, Any]] = []
    scan_info: dict[str, Any] | None = None
    domain_name: str | None = None

    for item in records:
        if not isinstance(item, dict):
            continue

        normalized = {
            str(key): _normalize_scalar(value)
            for key, value in item.items()
        }

        if str(normalized.get("type", "")).upper() == "SCANINFO":
            scan_info = normalized
            continue

        normalized_records.append(normalized)

        if domain_name is None:
            domain = normalized.get("domain")
            if isinstance(domain, str) and domain:
                domain_name = domain.rstrip(".").lower()

    return {
        "domain_name": domain_name,
        "records": normalized_records,
        "a_records": _address_values(normalized_records, "A"),
        "aaaa_records": _address_values(normalized_records, "AAAA"),
        "mx_records": _record_values(normalized_records, "MX"),
        "ns_records": _record_values(normalized_records, "NS"),
        "soa_records": _record_values(normalized_records, "SOA"),
        "txt_records": _text_values(normalized_records, "TXT"),
        "spf_records": _spf_values(normalized_records),
        "srv_records": _record_values(normalized_records, "SRV"),
        "cname_records": _record_values(normalized_records, "CNAME"),
        "scan_info": scan_info,
    }


def _normalize_scalar(value: Any) -> Any:
    if isinstance(value, tuple):
        return list(value)
    return value


def _records_of_type(
    records: list[dict[str, Any]],
    record_type: str,
) -> list[dict[str, Any]]:
    return [
        record
        for record in records
        if str(record.get("type", "")).upper() == record_type
    ]


def _address_values(
    records: list[dict[str, Any]],
    record_type: str,
) -> list[str]:
    values: list[str] = []
    for record in _records_of_type(records, record_type):
        address = record.get("address")
        if isinstance(address, str) and address and address not in values:
            values.append(address)
    return values


def _record_values(
    records: list[dict[str, Any]],
    record_type: str,
) -> list[dict[str, Any]]:
    return [dict(record) for record in _records_of_type(records, record_type)]


def _text_values(
    records: list[dict[str, Any]],
    record_type: str,
) -> list[str]:
    values: list[str] = []
    for record in _records_of_type(records, record_type):
        text = record.get("text")
        if isinstance(text, str) and text and text not in values:
            values.append(text)
    return values


def _spf_values(records: list[dict[str, Any]]) -> list[str]:
    values: list[str] = []
    for record in records:
        text = record.get("text")
        if (
            isinstance(text, str)
            and text.lower().startswith("v=spf1")
            and text not in values
        ):
            values.append(text)
    return values
