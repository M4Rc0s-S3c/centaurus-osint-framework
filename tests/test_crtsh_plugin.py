"""Tests for the crt.sh Certificate Transparency plugin adapter."""

from datetime import datetime, timezone

import pytest

from centaurus.evidence import EvidenceSource, RawObservation
from centaurus.plugins.base_plugin import BasePlugin
from centaurus.plugins.crtsh import Plugin
from centaurus.plugins.crtsh import plugin as crtsh_plugin


class FakeResponse:
    def __init__(self, data, *, json_error: Exception | None = None) -> None:
        self._data = data
        self._json_error = json_error
        self.status_checked = False

    def raise_for_status(self) -> None:
        self.status_checked = True

    def json(self):
        if self._json_error is not None:
            raise self._json_error
        return self._data


def test_crtsh_plugin_implements_base_contract() -> None:
    assert issubclass(Plugin, BasePlugin)


def test_crtsh_plugin_without_domain_returns_empty_observation(monkeypatch) -> None:
    calls = []
    monkeypatch.setattr(crtsh_plugin.httpx, "get", lambda *a, **k: calls.append((a, k)))

    observation = Plugin().execute({})

    assert isinstance(observation, RawObservation)
    assert observation.source is EvidenceSource.CRTSH
    assert observation.data == {}
    assert calls == []


def test_crtsh_plugin_queries_json_interface_with_wildcard(monkeypatch) -> None:
    captured = {}
    records = [
        {
            "issuer_ca_id": 1,
            "issuer_name": "Example CA",
            "common_name": "www.example.com",
            "name_value": "www.example.com\napi.example.com",
            "id": 100,
            "entry_timestamp": "2026-08-16T10:00:00",
            "not_before": "2026-08-16T09:00:00",
            "not_after": "2026-11-14T09:00:00",
            "serial_number": "01AB",
        }
    ]
    response = FakeResponse(records)

    def fake_get(url: str, **kwargs):
        captured["url"] = url
        captured["kwargs"] = kwargs
        return response

    monkeypatch.setattr(crtsh_plugin.httpx, "get", fake_get)

    observation = Plugin().execute({"domain": "Example.COM."})

    assert observation.source is EvidenceSource.CRTSH
    assert observation.data == {
        "domain": "example.com",
        "certificates": records,
    }
    assert captured["url"] == "https://crt.sh/"
    assert captured["kwargs"]["params"] == {
        "q": "%.example.com",
        "output": "json",
    }
    assert captured["kwargs"]["follow_redirects"] is True
    assert response.status_checked is True
    assert isinstance(observation.collected_at, datetime)
    assert observation.collected_at.tzinfo == timezone.utc


def test_crtsh_plugin_preserves_successful_zero_result(monkeypatch) -> None:
    monkeypatch.setattr(
        crtsh_plugin.httpx,
        "get",
        lambda *a, **k: FakeResponse([]),
    )

    observation = Plugin().execute({"domain": "example.com"})

    assert observation.data == {
        "domain": "example.com",
        "certificates": [],
    }


def test_crtsh_plugin_rejects_non_array_json(monkeypatch) -> None:
    monkeypatch.setattr(
        crtsh_plugin.httpx,
        "get",
        lambda *a, **k: FakeResponse({"unexpected": True}),
    )

    with pytest.raises(ValueError, match="JSON array of objects"):
        Plugin().execute({"domain": "example.com"})


def test_crtsh_plugin_rejects_non_object_array_members(monkeypatch) -> None:
    monkeypatch.setattr(
        crtsh_plugin.httpx,
        "get",
        lambda *a, **k: FakeResponse([{"id": 1}, "invalid"]),
    )

    with pytest.raises(ValueError, match="JSON array of objects"):
        Plugin().execute({"domain": "example.com"})


def test_crtsh_plugin_reports_invalid_json(monkeypatch) -> None:
    monkeypatch.setattr(
        crtsh_plugin.httpx,
        "get",
        lambda *a, **k: FakeResponse(None, json_error=ValueError("invalid")),
    )

    with pytest.raises(RuntimeError, match="invalid JSON"):
        Plugin().execute({"domain": "example.com"})
