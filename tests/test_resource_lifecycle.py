"""Resource-lifecycle tests for framework infrastructure boundaries."""

import json
from datetime import datetime, timezone
from types import SimpleNamespace

from centaurus.evidence import EvidenceSource, RawObservation
from centaurus.executor.execution import ExecutionTask
from centaurus.llm.ollama_provider import OllamaProvider
from centaurus.persistence.filesystem import (
    FilesystemEvidenceStore,
    FilesystemFindingStore,
    FilesystemRawObservationStore,
    FilesystemReportStore,
)
from centaurus.plugin_manager import PluginManager
from centaurus.plugins import BasePlugin
from centaurus.report import Report


class TrackingPlugin(BasePlugin):
    """Minimal plugin used to observe PluginManager loading behaviour."""

    def execute(self, parameters: dict) -> RawObservation:
        return RawObservation(
            source=EvidenceSource.WHOIS,
            data={"domain": parameters["domain"]},
            collected_at=datetime.now(timezone.utc),
        )


def test_plugin_manager_does_not_load_plugins_during_construction(monkeypatch):
    """Creating PluginManager must not import any plugin implementation."""

    calls = []

    def fake_import(module_name):
        calls.append(module_name)
        return SimpleNamespace(Plugin=TrackingPlugin)

    monkeypatch.setattr(
        "centaurus.plugin_manager.plugin_manager.importlib.import_module",
        fake_import,
    )

    PluginManager()

    assert calls == []


def test_plugin_manager_loads_plugin_only_when_task_is_executed(monkeypatch):
    """Plugin code is loaded lazily when an ExecutionTask reaches execution."""

    calls = []

    def fake_import(module_name):
        calls.append(module_name)
        return SimpleNamespace(Plugin=TrackingPlugin)

    monkeypatch.setattr(
        "centaurus.plugin_manager.plugin_manager.importlib.import_module",
        fake_import,
    )
    monkeypatch.setattr(
        PluginManager,
        "_validate_plugin",
        lambda self, plugin_name: True,
    )

    manager = PluginManager()
    task = ExecutionTask(
        plugin_id="tracking",
        parameters={"domain": "example.com"},
    )

    result = manager.execute(task)

    assert calls == ["centaurus.plugins.tracking"]
    assert result.data == {"domain": "example.com"}


def test_owned_ollama_http_client_is_created_lazily_and_closed(monkeypatch):
    """Ollama transport exists only for the duration of an owned request."""

    events = []

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "response": json.dumps(
                    {
                        "executive_summary": {
                            "text": "No Findings are present in the supplied Report.",
                            "supporting_finding_refs": [],
                        },
                        "finding_summaries": [],
                        "risk_considerations": [],
                        "recommendations": [],
                    }
                )
            }

    class FakeClient:
        def __init__(self, *, timeout):
            events.append(("created", timeout))

        def post(self, url, json):
            events.append(("post", url))
            return FakeResponse()

        def close(self):
            events.append(("closed", None))

    monkeypatch.setattr(
        "centaurus.llm.ollama_provider.httpx.Client",
        FakeClient,
    )

    provider = OllamaProvider(
        base_url="http://ollama",
        timeout=12,
    )

    assert events == []

    rendered = provider.generate(
        Report(
            investigation_id="inv-resource",
            generated_at=datetime(2026, 8, 20, 12, 30, tzinfo=timezone.utc),
            target="example.org",
            target_type="DOMAIN",
            intent="public_exposure_assessment",
            findings=(),
        ),
    )

    assert "Analyst-assistance view" in rendered

    assert events == [
        ("created", 12),
        ("post", "http://ollama/api/generate"),
        ("closed", None),
    ]


def test_filesystem_stores_do_not_create_workspace_during_construction(tmp_path):
    """Filesystem resources are acquired on persist, not at store construction."""

    workspace = tmp_path / "workspace"

    stores = (
        FilesystemRawObservationStore(workspace),
        FilesystemEvidenceStore(workspace),
        FilesystemFindingStore(workspace),
        FilesystemReportStore(workspace),
    )

    assert len(stores) == 4
    assert not workspace.exists()
