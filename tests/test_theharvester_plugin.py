"""Tests for the theHarvester passive OSINT plugin adapter."""

import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest

from centaurus.evidence import EvidenceSource, RawObservation
from centaurus.plugins.base_plugin import BasePlugin
from centaurus.plugins.theharvester import Plugin
from centaurus.plugins.theharvester import plugin as theharvester_plugin


def test_theharvester_plugin_implements_base_contract() -> None:
    assert issubclass(Plugin, BasePlugin)


def test_theharvester_plugin_without_domain_returns_empty_observation(monkeypatch) -> None:
    calls = []
    monkeypatch.setattr(
        theharvester_plugin.subprocess,
        "run",
        lambda *a, **k: calls.append((a, k)),
    )

    observation = Plugin().execute({})

    assert isinstance(observation, RawObservation)
    assert observation.source is EvidenceSource.THEHARVESTER
    assert observation.data == {}
    assert calls == []


def test_theharvester_plugin_runs_bounded_passive_sources_and_reads_json(monkeypatch) -> None:
    captured = {}
    report = {
        "cmd": "theHarvester ...",
        "hosts": ["www.example.com", "api.example.com"],
        "emails": ["security@example.com"],
        "ips": ["192.0.2.10"],
        "interesting_urls": ["https://www.example.com/login"],
        "asns": ["AS64500"],
        "shodan": [],
    }

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        report_base = Path(command[command.index("-f") + 1])
        report_base.with_suffix(".json").write_text(
            json.dumps(report),
            encoding="utf-8",
        )
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(theharvester_plugin.subprocess, "run", fake_run)

    observation = Plugin().execute({"domain": "Example.COM."})

    assert observation.source is EvidenceSource.THEHARVESTER
    assert observation.data == {
        "domain": "example.com",
        "sources": [
            "duckduckgo",
            "rapiddns",
            "urlscan",
            "waybackarchive",
        ],
        "limit": 100,
        "report": report,
    }
    command = captured["command"]
    assert command[:3] == ["theHarvester", "-d", "example.com"]
    assert command[command.index("-l") + 1] == "100"
    assert command[command.index("-b") + 1] == (
        "duckduckgo,rapiddns,urlscan,waybackarchive"
    )
    assert "-q" in command
    assert "-c" not in command
    assert "-n" not in command
    assert "-r" not in command
    assert "-t" not in command
    assert "-a" not in command
    assert "-s" not in command
    assert "--screenshot" not in command

    kwargs = captured["kwargs"]
    assert kwargs["check"] is False
    assert kwargs["capture_output"] is True
    assert kwargs["text"] is True
    assert kwargs["timeout"] == 300
    assert kwargs["shell"] is False
    assert kwargs["cwd"] == kwargs["env"]["HOME"]
    assert kwargs["cwd"].startswith(str(Path(command[command.index("-f") + 1]).parent))


def test_theharvester_plugin_reports_missing_executable(monkeypatch) -> None:
    def fake_run(*args, **kwargs):
        raise FileNotFoundError("missing")

    monkeypatch.setattr(theharvester_plugin.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="executable is not available"):
        Plugin().execute({"domain": "example.com"})


def test_theharvester_plugin_reports_timeout(monkeypatch) -> None:
    def fake_run(command, **kwargs):
        raise subprocess.TimeoutExpired(command, timeout=kwargs["timeout"])

    monkeypatch.setattr(theharvester_plugin.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="timed out"):
        Plugin().execute({"domain": "example.com"})


def test_theharvester_plugin_reports_nonzero_exit(monkeypatch) -> None:
    monkeypatch.setattr(
        theharvester_plugin.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(
            returncode=2,
            stdout="",
            stderr="upstream failed",
        ),
    )

    with pytest.raises(RuntimeError, match="upstream failed"):
        Plugin().execute({"domain": "example.com"})


def test_theharvester_plugin_requires_json_report(monkeypatch) -> None:
    monkeypatch.setattr(
        theharvester_plugin.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=0, stdout="", stderr=""),
    )

    with pytest.raises(RuntimeError, match="expected JSON report"):
        Plugin().execute({"domain": "example.com"})


def test_theharvester_plugin_reports_invalid_json(monkeypatch) -> None:
    def fake_run(command, **kwargs):
        report_base = Path(command[command.index("-f") + 1])
        report_base.with_suffix(".json").write_text("not-json", encoding="utf-8")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(theharvester_plugin.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="invalid JSON report"):
        Plugin().execute({"domain": "example.com"})


def test_theharvester_plugin_rejects_non_object_json(monkeypatch) -> None:
    def fake_run(command, **kwargs):
        report_base = Path(command[command.index("-f") + 1])
        report_base.with_suffix(".json").write_text("[]", encoding="utf-8")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(theharvester_plugin.subprocess, "run", fake_run)

    with pytest.raises(ValueError, match="must be an object"):
        Plugin().execute({"domain": "example.com"})
