"""Tests for the Sublist3r plugin adapter."""

import subprocess
from types import SimpleNamespace

import pytest

from centaurus.evidence import EvidenceSource, RawObservation
from centaurus.plugins.base_plugin import BasePlugin
from centaurus.plugins.sublist3r import Plugin
from centaurus.plugins.sublist3r import plugin as sublist3r_plugin


def test_sublist3r_plugin_implements_base_contract() -> None:
    assert issubclass(Plugin, BasePlugin)


def test_sublist3r_plugin_without_domain_returns_empty_observation(monkeypatch) -> None:
    calls = []
    monkeypatch.setattr(sublist3r_plugin.subprocess, "run", lambda *a, **k: calls.append((a, k)))

    observation = Plugin().execute({})

    assert isinstance(observation, RawObservation)
    assert observation.source is EvidenceSource.SUBLIST3R
    assert observation.data == {}
    assert calls == []


def test_sublist3r_plugin_executes_passive_scan_and_reads_output(monkeypatch) -> None:
    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        output_path = command[command.index("-o") + 1]
        with open(output_path, "w", encoding="utf-8") as output:
            output.write("WWW.EXAMPLE.COM\n")
            output.write("api.example.com\n")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(sublist3r_plugin.subprocess, "run", fake_run)

    observation = Plugin().execute({"domain": "Example.COM."})

    assert observation.source is EvidenceSource.SUBLIST3R
    assert observation.data == {
        "domain": "example.com",
        "subdomains": ["WWW.EXAMPLE.COM", "api.example.com"],
    }
    assert captured["command"][0] == "sublist3r"
    assert captured["command"][1:3] == ["-d", "example.com"]
    assert "-o" in captured["command"]
    assert "-n" in captured["command"]
    assert "-b" not in captured["command"]
    assert "-p" not in captured["command"]
    assert captured["kwargs"]["check"] is False
    assert captured["kwargs"]["capture_output"] is True


def test_sublist3r_plugin_does_not_use_shell_command(monkeypatch) -> None:
    def fake_run(command, **kwargs):
        assert isinstance(command, list)
        assert "shell" not in kwargs
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(sublist3r_plugin.subprocess, "run", fake_run)

    Plugin().execute({"domain": "example.com;echo injected"})


def test_sublist3r_plugin_accepts_successful_zero_result(monkeypatch) -> None:
    monkeypatch.setattr(
        sublist3r_plugin.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=0, stdout="", stderr=""),
    )

    observation = Plugin().execute({"domain": "example.com"})

    assert observation.data == {"domain": "example.com", "subdomains": []}


def test_sublist3r_plugin_reports_missing_executable(monkeypatch) -> None:
    def missing(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(sublist3r_plugin.subprocess, "run", missing)

    with pytest.raises(RuntimeError, match="executable is not available"):
        Plugin().execute({"domain": "example.com"})


def test_sublist3r_plugin_reports_process_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        sublist3r_plugin.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=2, stdout="", stderr="failure"),
    )

    with pytest.raises(RuntimeError, match="Sublist3r execution failed.*failure"):
        Plugin().execute({"domain": "example.com"})


def test_sublist3r_plugin_reports_timeout(monkeypatch) -> None:
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=180)

    monkeypatch.setattr(sublist3r_plugin.subprocess, "run", timeout)

    with pytest.raises(RuntimeError, match="timed out"):
        Plugin().execute({"domain": "example.com"})
