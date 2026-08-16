"""Deterministic normalization of RDAP domain registration data."""

from typing import Any


def normalize_rdap_data(
    data: dict[str, Any],
) -> dict[str, Any]:
    """Normalize one RDAP response into the registration Evidence vocabulary.

    The transformation maps standardized RDAP representation to the stable
    fields already consumed by registration Rules. It does not infer risk or
    create conclusions.
    """

    if not data:
        return {}

    return {
        "domain_name": data.get("ldhName"),
        "handle": data.get("handle"),
        "status": _normalize_list(data.get("status")),
        "registrar": _entity_name(data.get("entities"), "registrar"),
        "registrant_name": _entity_name(data.get("entities"), "registrant"),
        "creation_date": _event_date(data.get("events"), "registration"),
        "expiration_date": _event_date(data.get("events"), "expiration"),
        "updated_date": _event_date(data.get("events"), "last changed"),
        "name_servers": _name_servers(data.get("nameservers")),
        "dnssec": _dnssec_status(data.get("secureDNS")),
        "start_address": data.get("startAddress"),
        "end_address": data.get("endAddress"),
        "ip_version": data.get("ipVersion"),
        "name": data.get("name"),
        "type": data.get("type"),
        "country": data.get("country"),
    }


def _normalize_list(value: Any) -> list[Any] | None:
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def _event_date(events: Any, action: str) -> Any:
    if not isinstance(events, list):
        return None

    for event in events:
        if isinstance(event, dict) and event.get("eventAction") == action:
            return event.get("eventDate")

    return None


def _name_servers(nameservers: Any) -> list[str] | None:
    if not isinstance(nameservers, list):
        return None

    values = [
        item.get("ldhName")
        for item in nameservers
        if isinstance(item, dict) and item.get("ldhName")
    ]

    return values or None


def _dnssec_status(secure_dns: Any) -> str | None:
    if not isinstance(secure_dns, dict):
        return None

    signed = secure_dns.get("delegationSigned")
    if signed is True:
        return "signedDelegation"
    if signed is False:
        return "unsigned"
    return None


def _entity_name(entities: Any, role: str) -> str | None:
    if not isinstance(entities, list):
        return None

    for entity in entities:
        if not isinstance(entity, dict):
            continue
        roles = entity.get("roles")
        if not isinstance(roles, list) or role not in roles:
            continue

        vcard_name = _vcard_full_name(entity.get("vcardArray"))
        if vcard_name is not None:
            return vcard_name

        handle = entity.get("handle")
        if isinstance(handle, str) and handle:
            return handle

    return None


def _vcard_full_name(vcard_array: Any) -> str | None:
    if (
        not isinstance(vcard_array, list)
        or len(vcard_array) < 2
        or not isinstance(vcard_array[1], list)
    ):
        return None

    for property_value in vcard_array[1]:
        if (
            isinstance(property_value, list)
            and len(property_value) >= 4
            and property_value[0] == "fn"
        ):
            value = property_value[3]
            if isinstance(value, str) and value:
                return value

    return None
