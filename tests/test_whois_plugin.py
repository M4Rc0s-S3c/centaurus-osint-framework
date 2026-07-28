"""
Unit tests for the WHOIS plugin.
"""

from centaurus.plugins.whois.plugin import Plugin


def test_whois_plugin_can_be_created() -> None:
    """
    The WHOIS plugin can be instantiated.
    """

    plugin = Plugin()

    assert plugin is not None


def test_whois_plugin_returns_structured_result() -> None:
    """
    The WHOIS plugin returns a structured result.
    """

    plugin = Plugin()

    result = plugin.execute(
        {
            "domain": "example.com",
        }
    )

    assert isinstance(result, dict)

    assert result["plugin"] == "whois"
    assert result["status"] == "completed"

    assert result["data"]["domain"] == "example.com"
    assert result["data"]["registrar"] == "Example Registrar"
    assert result["data"]["creation_date"] == "1995-08-14"


def test_whois_plugin_uses_unknown_domain_by_default() -> None:
    """
    The WHOIS plugin handles missing domain parameters.
    """

    plugin = Plugin()

    result = plugin.execute({})

    assert result["data"]["domain"] == "unknown"
