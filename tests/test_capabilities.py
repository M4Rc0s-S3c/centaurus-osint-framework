from centaurus.capabilities import (
    DEFERRED_TARGET_CAPABILITIES,
    IMPLEMENTED_TOOLS,
    OPERATIONAL_TARGET_CAPABILITIES,
    PUBLIC_EXPOSURE_ASSESSMENT,
    SUPPORTED_INTENTS,
    SUPPORTED_TARGET_TYPES,
    get_operational_target_capability,
)


def test_distribution_capability_catalog_matches_operational_plans() -> None:
    assert SUPPORTED_INTENTS == frozenset({PUBLIC_EXPOSURE_ASSESSMENT})
    assert SUPPORTED_TARGET_TYPES == frozenset({"DOMAIN", "IP"})

    domain = get_operational_target_capability("domain")
    assert domain.status == "full"
    assert len(domain.tasks) == 7
    assert domain.tools == (
        "whois",
        "rdap",
        "dnsrecon",
        "sublist3r",
        "crtsh",
        "theharvester",
    )

    ip = get_operational_target_capability("IP")
    assert ip.status == "limited"
    assert len(ip.tasks) == 1
    assert ip.tools == ("rdap",)

    assert IMPLEMENTED_TOOLS == (
        "whois",
        "rdap",
        "dnsrecon",
        "sublist3r",
        "crtsh",
        "theharvester",
    )
    assert tuple(cap.target_type for cap in OPERATIONAL_TARGET_CAPABILITIES) == (
        "DOMAIN",
        "IP",
    )


def test_distribution_catalog_marks_email_and_certificate_non_operational() -> None:
    assert tuple(cap.target_type for cap in DEFERRED_TARGET_CAPABILITIES) == (
        "EMAIL",
        "CERTIFICATE",
    )
    assert all(not cap.operational for cap in DEFERRED_TARGET_CAPABILITIES)


def test_capability_templates_build_the_same_domain_task_contract() -> None:
    domain = get_operational_target_capability("DOMAIN")
    tasks = tuple(template.build("example.com") for template in domain.tasks)

    assert [(task.plugin_id, task.parameters) for task in tasks] == [
        ("whois", {"domain": "example.com"}),
        ("rdap", {"domain": "example.com"}),
        ("dnsrecon", {"domain": "example.com"}),
        ("dnsrecon", {"domain": "example.com", "mode": "dmarc"}),
        ("sublist3r", {"domain": "example.com"}),
        ("crtsh", {"domain": "example.com"}),
        ("theharvester", {"domain": "example.com"}),
    ]
