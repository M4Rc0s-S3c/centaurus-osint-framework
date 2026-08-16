"""Tests for the DNSRecon plugin adapter."""

import json
import subprocess
from types import SimpleNamespace

import pytest

from centaurus.evidence import EvidenceSource, RawObservation
from centaurus.plugins.base_plugin import BasePlugin
from centaurus.plugins.dnsrecon import Plugin
from centaurus.plugins.dnsrecon import plugin as dnsrecon_plugin


def test_dnsrecon_plugin_implements_base_contract() -> None:
    assert issubclass(Plugin, BasePlugin)


def test_dnsrecon_plugin_without_domain_returns_empty_observation(monkeypatch) -> None:
    calls = []
    monkeypatch.setattr(dnsrecon_plugin.subprocess, "run", lambda *a, **k: calls.append((a, k)))

    observation = Plugin().execute({})

    assert isinstance(observation, RawObservation)
    assert observation.source is EvidenceSource.DNSRECON
    assert observation.data == {}
    assert calls == []


def test_dnsrecon_plugin_executes_standard_scan_and_reads_json(monkeypatch) -> None:
    captured = {}
    raw_records = [
        {"type": "ScanInfo", "arguments": "dnsrecon ...", "date": "2026-08-16"},
        {"domain": "example.com", "type": "A", "name": "example.com", "address": "192.0.2.10"},
    ]

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        output_path = command[command.index("-j") + 1]
        with open(output_path, "w", encoding="utf-8") as output:
            json.dump(raw_records, output)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(dnsrecon_plugin.subprocess, "run", fake_run)

    observation = Plugin().execute({"domain": "Example.COM."})

    assert observation.source is EvidenceSource.DNSRECON
    assert observation.data == {"records": raw_records}
    assert captured["command"][0] == "dnsrecon"
    assert captured["command"][1:5] == ["-d", "example.com", "-t", "std"]
    assert "--disable_check_recursion" in captured["command"]
    assert "--disable_check_bindversion" in captured["command"]
    assert captured["kwargs"]["check"] is False
    assert captured["kwargs"]["capture_output"] is True


def test_dnsrecon_plugin_does_not_use_shell_command(monkeypatch) -> None:
    def fake_run(command, **kwargs):
        assert isinstance(command, list)
        assert "shell" not in kwargs
        output_path = command[command.index("-j") + 1]
        with open(output_path, "w", encoding="utf-8") as output:
            json.dump([], output)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(dnsrecon_plugin.subprocess, "run", fake_run)

    Plugin().execute({"domain": "example.com;echo injected"})


def test_dnsrecon_plugin_reports_missing_executable(monkeypatch) -> None:
    def missing(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(dnsrecon_plugin.subprocess, "run", missing)

    with pytest.raises(RuntimeError, match="executable is not available"):
        Plugin().execute({"domain": "example.com"})


def test_dnsrecon_plugin_reports_process_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        dnsrecon_plugin.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=2, stdout="", stderr="failure"),
    )

    with pytest.raises(RuntimeError, match="DNSRecon execution failed.*failure"):
        Plugin().execute({"domain": "example.com"})


def test_dnsrecon_plugin_reports_timeout(monkeypatch) -> None:
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=120)

    monkeypatch.setattr(dnsrecon_plugin.subprocess, "run", timeout)

    with pytest.raises(RuntimeError, match="timed out"):
        Plugin().execute({"domain": "example.com"})
