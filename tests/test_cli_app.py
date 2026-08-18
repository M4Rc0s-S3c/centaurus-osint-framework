from io import StringIO
from types import SimpleNamespace

import pytest
from rich.console import Console
from typer.testing import CliRunner

import centaurus.cli.app as cli_app
from centaurus.llm.exceptions import LLMProviderError


runner = CliRunner()


class FakeCLI:
    def __init__(self, investigation=None, *, error=None):
        self.investigation = investigation or make_investigation()
        self.error = error
        self.requests = []
        self.started = False
        self.stopped = False

    def submit(self, user_input):
        self.requests.append(user_input)
        if self.error is not None:
            raise self.error
        return self.investigation

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True


class FakeCore:
    def __init__(
        self,
        *,
        execution_status="completed",
        failures=(),
        presentation="Structured analyst presentation",
    ):
        self.last_execution_status = execution_status
        self.last_execution_failures = failures
        self.last_llm_output = presentation


class FakeSession:
    def __init__(self, values):
        self._values = iter(values)

    def prompt(self, message):
        return next(self._values)


def make_investigation(*, status="completed", findings=()):
    report = None if status == "failed" else SimpleNamespace(findings=findings)
    return SimpleNamespace(
        id="INV-CLI-001",
        target="example.com",
        target_type="DOMAIN",
        intent="public_exposure_assessment",
        status=SimpleNamespace(value=status),
        evidences=(object(), object()),
        findings=findings,
        report=report,
    )


def make_console():
    stream = StringIO()
    return Console(file=stream, force_terminal=False, width=120), stream


def test_cli_help_exposes_final_commands():
    result = runner.invoke(cli_app.app, ["--help"])

    assert result.exit_code == 0
    assert "investigate" in result.stdout
    assert "shell" in result.stdout


def test_investigate_command_forwards_natural_language_and_renders_result(monkeypatch):
    finding = SimpleNamespace(
        rule=SimpleNamespace(id="RL-007"),
        conclusion="No SPF policy was observed.",
    )
    fake_cli = FakeCLI(investigation=make_investigation(findings=(finding,)))
    monkeypatch.setattr(cli_app, "build_runtime", lambda: (fake_cli, FakeCore()))

    result = runner.invoke(
        cli_app.app,
        ["investigate", "Investiga", "la", "exposición", "de", "example.com"],
    )

    assert result.exit_code == cli_app.EXIT_OK
    assert fake_cli.requests == ["Investiga la exposición de example.com"]
    assert "INV-CLI-001" in result.stdout
    assert "RL-007" in result.stdout
    assert "Structured analyst presentation" in result.stdout


def test_partial_execution_is_visible_but_returns_success(monkeypatch):
    failure = SimpleNamespace(
        task_index=4,
        plugin_id="crtsh_lookup",
        category="timeout",
        message="request timed out",
    )
    fake_cli = FakeCLI()
    fake_core = FakeCore(execution_status="partial", failures=(failure,))
    monkeypatch.setattr(cli_app, "build_runtime", lambda: (fake_cli, fake_core))

    result = runner.invoke(cli_app.app, ["investigate", "Investiga", "example.com"])

    assert result.exit_code == cli_app.EXIT_OK
    assert "PARTIAL" in result.stdout
    assert "crtsh_lookup" in result.stdout
    assert "timeout" in result.stdout


def test_failed_investigation_returns_operational_failure_code(monkeypatch):
    failure = SimpleNamespace(
        task_index=1,
        plugin_id="whois",
        category="unavailable",
        message="tool unavailable",
    )
    fake_cli = FakeCLI(investigation=make_investigation(status="failed"))
    fake_core = FakeCore(
        execution_status="failed",
        failures=(failure,),
        presentation=None,
    )
    monkeypatch.setattr(cli_app, "build_runtime", lambda: (fake_cli, fake_core))

    result = runner.invoke(cli_app.app, ["investigate", "Investiga", "example.com"])

    assert result.exit_code == cli_app.EXIT_OPERATIONAL_FAILURE
    assert "FAILED" in result.stdout
    assert "did not produce a final Report" in result.stdout


def test_invalid_request_returns_usage_code(monkeypatch):
    fake_cli = FakeCLI(error=ValueError("unable to detect a supported target"))
    monkeypatch.setattr(cli_app, "build_runtime", lambda: (fake_cli, FakeCore()))

    result = runner.invoke(cli_app.app, ["investigate", "investiga", "esto"])

    assert result.exit_code == cli_app.EXIT_INVALID_REQUEST
    assert "Invalid request" in result.stdout


def test_llm_interpretation_failure_returns_operational_failure_code(monkeypatch):
    fake_cli = FakeCLI(error=LLMProviderError("Ollama unavailable"))
    monkeypatch.setattr(cli_app, "build_runtime", lambda: (fake_cli, FakeCore()))

    result = runner.invoke(cli_app.app, ["investigate", "Investiga", "example.com"])

    assert result.exit_code == cli_app.EXIT_OPERATIONAL_FAILURE
    assert "LLM service error" in result.stdout


def test_unexpected_error_returns_internal_error_code(monkeypatch):
    fake_cli = FakeCLI(error=RuntimeError("unexpected runtime failure"))
    monkeypatch.setattr(cli_app, "build_runtime", lambda: (fake_cli, FakeCore()))

    result = runner.invoke(cli_app.app, ["investigate", "Investiga", "example.com"])

    assert result.exit_code == cli_app.EXIT_INTERNAL_ERROR
    assert "CENTAURUS execution error" in result.stdout


def test_execute_request_falls_back_to_deterministic_report_when_llm_output_missing():
    fake_cli = FakeCLI()
    fake_core = FakeCore(presentation=None)
    console, stream = make_console()

    exit_code = cli_app.execute_request(
        fake_cli, fake_core, "Investiga example.com", console
    )

    assert exit_code == cli_app.EXIT_OK
    assert "authoritative persisted result" in stream.getvalue()


def test_shell_processes_requests_and_stops_without_persistent_history():
    fake_cli = FakeCLI()
    console, stream = make_console()
    session = FakeSession(["/help", "Investiga example.com", "/exit"])

    exit_code = cli_app.run_shell(fake_cli, FakeCore(), console, session=session)

    assert exit_code == cli_app.EXIT_OK
    assert fake_cli.started is True
    assert fake_cli.stopped is True
    assert fake_cli.requests == ["Investiga example.com"]
    assert "/exit" in stream.getvalue()


def test_shell_continues_after_invalid_request():
    class RecoveringCLI(FakeCLI):
        def submit(self, user_input):
            self.requests.append(user_input)
            if len(self.requests) == 1:
                raise ValueError("bad request")
            return self.investigation

    fake_cli = RecoveringCLI()
    console, stream = make_console()
    session = FakeSession(["bad request", "Investiga example.com", "quit"])

    exit_code = cli_app.run_shell(fake_cli, FakeCore(), console, session=session)

    assert exit_code == cli_app.EXIT_OK
    assert fake_cli.requests == ["bad request", "Investiga example.com"]
    assert "Invalid request" in stream.getvalue()
