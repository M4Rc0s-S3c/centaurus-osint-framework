from io import StringIO

from rich.console import Console

from centaurus.cli.cli import CLI
from centaurus.cli.progress import RichRuntimeProgressReporter
from centaurus.core import Core
from centaurus.executor.execution import ExecutionPlan, ExecutionTask
from centaurus.executor.executor import Executor
from centaurus.exceptions import PluginExecutionError
from centaurus.investigation import Investigation
from centaurus.observability import RuntimeProgressEvent


class RecordingRuntimeProgressReporter:
    def __init__(self) -> None:
        self.started = 0
        self.stopped = 0
        self.events = []

    def start(self) -> None:
        self.started += 1

    def publish(self, event: RuntimeProgressEvent) -> None:
        self.events.append(event)

    def stop(self) -> None:
        self.stopped += 1


class FakeStore:
    def persist_raw(self, *args):
        return None

    def persist_evidence(self, *args):
        return None

    def persist_finding(self, *args):
        return None

    def persist_report(self, *args):
        return None

    def persist_failure(self, *args):
        return None


class FakeLLMManager:
    def generate(self, report):
        return "presentation"


class FakeInterpreter:
    def __init__(self, request) -> None:
        self.request = request

    def interpret(self, user_input):
        return self.request


class FakeCore:
    def __init__(self) -> None:
        self.received = []

    def submit_request(self, request, *, analyst_question=None):
        self.received.append((request, analyst_question))
        return "investigation"


class SelectivePluginManager:
    def __init__(self, failing_plugin_id: str | None = None) -> None:
        self.failing_plugin_id = failing_plugin_id

    def execute(self, task):
        if task.plugin_id == self.failing_plugin_id:
            raise PluginExecutionError(task.plugin_id, "tool failed")
        return {"plugin_id": task.plugin_id}


def test_cli_owns_progress_session_around_pre_core_interpretation():
    request = object()
    reporter = RecordingRuntimeProgressReporter()
    core = FakeCore()
    cli = CLI(
        core,
        request_interpreter=FakeInterpreter(request),
        progress_reporter=reporter,
    )

    result = cli.submit("Investiga example.com")

    assert result == "investigation"
    assert reporter.started == 1
    assert reporter.stopped == 1
    assert reporter.events[0].message == "Interpretando la petición"
    assert core.received == [(request, "Investiga example.com")]


def test_executor_returns_task_lifecycle_facts_through_callback():
    notifications = []

    def callback(state, task_index, task_total, task, failure):
        notifications.append(
            (state, task_index, task_total, task.plugin_id, failure)
        )

    plan = ExecutionPlan(investigation_id="INV-PROGRESS")
    plan.tasks.extend(
        [
            ExecutionTask("whois", {"domain": "example.com"}),
            ExecutionTask("crtsh", {"domain": "example.com"}),
        ]
    )
    executor = Executor(
        plugin_manager=SelectivePluginManager("crtsh"),
        progress_callback=callback,
    )

    result = executor.execute(plan)

    assert result["status"] == "partial"
    assert [(item[0], item[1], item[2], item[3]) for item in notifications] == [
        ("started", 1, 2, "whois"),
        ("succeeded", 1, 2, "whois"),
        ("started", 2, 2, "crtsh"),
        ("failed", 2, 2, "crtsh"),
    ]
    assert notifications[-1][4] is result["failures"][0]


def test_core_coordinates_runtime_phases_and_task_progress(monkeypatch):
    reporter = RecordingRuntimeProgressReporter()
    store = FakeStore()
    core = Core(
        raw_observation_store=store,
        evidence_store=store,
        report_store=store,
        finding_store=store,
        execution_failure_store=store,
        llm_manager=FakeLLMManager(),
        rules=(),
        progress_reporter=reporter,
    )

    def fake_execute(self, task):
        if task.plugin_id == "crtsh":
            raise PluginExecutionError("crtsh", "upstream unavailable")
        return {"plugin_id": task.plugin_id}

    from centaurus.plugin_manager.plugin_manager import PluginManager

    monkeypatch.setattr(PluginManager, "execute", fake_execute)

    investigation = Investigation(
        target="example.com",
        target_type="DOMAIN",
        intent="public_exposure_assessment",
    )
    core.run_investigation(investigation)

    messages = [event.message for event in reporter.events]
    assert messages[0] == "Planificando Investigation"
    assert "Preparando adquisición · 7 tareas" in messages
    assert "Persistiendo observaciones RAW" in messages
    assert "Normalizando Evidence" in messages
    assert "Evaluando Rules" in messages
    assert "Generando Report" in messages
    assert "Preparando asistencia analítica LLM" in messages
    assert messages[-2] == "Finalizando Investigation"
    assert reporter.events[-1].kind == "session_completed"

    task_events = [event for event in reporter.events if event.task_index is not None]
    assert any(
        event.kind == "task_started"
        and event.task_index == 3
        and event.plugin_id == "dnsrecon"
        and event.task_variant is None
        for event in task_events
    )
    assert any(
        event.kind == "task_started"
        and event.task_index == 4
        and event.plugin_id == "dnsrecon"
        and event.task_variant == "dmarc"
        for event in task_events
    )
    assert any(
        event.kind == "task_failed"
        and event.plugin_id == "crtsh"
        and event.failure_category == "execution_error"
        for event in task_events
    )
    assert core.last_execution_status == "partial"


def test_rich_progress_shows_spinner_context_elapsed_and_partial_failure():
    stream = StringIO()
    console = Console(
        file=stream,
        force_terminal=True,
        color_system=None,
        width=120,
    )
    reporter = RichRuntimeProgressReporter(console)

    reporter.start()
    reporter.publish(RuntimeProgressEvent(message="Planificando Investigation"))
    reporter.publish(
        RuntimeProgressEvent(
            message="Adquiriendo",
            kind="task_started",
            task_index=4,
            task_total=7,
            plugin_id="dnsrecon",
            task_variant="dmarc",
        )
    )
    reporter.publish(
        RuntimeProgressEvent(
            message="Adquiriendo",
            kind="task_failed",
            task_index=6,
            task_total=7,
            plugin_id="crtsh",
            failure_category="upstream_error",
        )
    )
    reporter.stop()

    output = stream.getvalue()
    assert "4/7" in output
    assert "DNSRecon" in output
    assert "DMARC" in output
    assert "6/7" in output
    assert "crt.sh" in output
    assert "upstream_error" in output
    assert "continuando con cobertura parcial" in output
    assert "%" not in output
    assert "ETA" not in output


def test_rich_progress_persists_completed_tasks_and_fast_phases():
    stream = StringIO()
    console = Console(
        file=stream,
        force_terminal=True,
        color_system=None,
        width=120,
    )
    reporter = RichRuntimeProgressReporter(console)

    reporter.start()
    reporter.publish(RuntimeProgressEvent(message="Interpretando la petición"))
    reporter.publish(RuntimeProgressEvent(message="Planificando Investigation"))
    reporter.publish(RuntimeProgressEvent(message="Preparando adquisición · 7 tareas"))
    reporter.publish(
        RuntimeProgressEvent(
            message="Adquiriendo",
            kind="task_started",
            task_index=1,
            task_total=7,
            plugin_id="whois",
        )
    )
    reporter.publish(
        RuntimeProgressEvent(
            message="Adquiriendo",
            kind="task_succeeded",
            task_index=1,
            task_total=7,
            plugin_id="whois",
        )
    )
    reporter.publish(RuntimeProgressEvent(message="Persistiendo observaciones RAW"))
    reporter.publish(RuntimeProgressEvent(message="Normalizando Evidence"))
    reporter.publish(RuntimeProgressEvent(message="Evaluando Rules"))
    reporter.publish(RuntimeProgressEvent(message="Generando Report"))
    reporter.publish(RuntimeProgressEvent(message="Preparando asistencia analítica LLM"))
    reporter.publish(RuntimeProgressEvent(message="Finalizando Investigation"))
    reporter.publish(
        RuntimeProgressEvent(
            message="Sesión de progreso completada",
            kind="session_completed",
        )
    )
    reporter.stop()

    output = stream.getvalue()
    assert "✓ Interpretando la petición" in output
    assert "✓ Planificando Investigation" in output
    assert "✓ Preparando adquisición · 7 tareas" in output
    assert "✓ 1/7 · WHOIS" in output
    assert "✓ Persistiendo observaciones RAW" in output
    assert "✓ Normalizando Evidence" in output
    assert "✓ Evaluando Rules" in output
    assert "✓ Generando Report" in output
    assert "✓ Preparando asistencia analítica LLM" in output
    assert "✓ Finalizando Investigation" in output


def test_rich_progress_does_not_mark_incomplete_phase_as_success_on_stop():
    stream = StringIO()
    console = Console(
        file=stream,
        force_terminal=True,
        color_system=None,
        width=120,
    )
    reporter = RichRuntimeProgressReporter(console)

    reporter.start()
    reporter.publish(RuntimeProgressEvent(message="Interpretando la petición"))
    reporter.stop()

    output = stream.getvalue()
    assert "✓ Interpretando la petición" not in output


def test_rich_progress_is_silent_for_non_interactive_output():
    stream = StringIO()
    console = Console(file=stream, force_terminal=False, width=120)
    reporter = RichRuntimeProgressReporter(console)

    reporter.start()
    reporter.publish(RuntimeProgressEvent(message="Planificando Investigation"))
    reporter.stop()

    assert stream.getvalue() == ""


class FailingRuntimeProgressReporter:
    def start(self) -> None:
        raise RuntimeError("presentation unavailable")

    def publish(self, event: RuntimeProgressEvent) -> None:
        raise RuntimeError("presentation unavailable")

    def stop(self) -> None:
        raise RuntimeError("presentation unavailable")


def test_progress_presentation_failure_does_not_block_cli_submission():
    request = object()
    core = FakeCore()
    cli = CLI(
        core,
        request_interpreter=FakeInterpreter(request),
        progress_reporter=FailingRuntimeProgressReporter(),
    )

    result = cli.submit("Investiga example.com")

    assert result == "investigation"
    assert core.received == [(request, "Investiga example.com")]


def test_progress_presentation_failure_does_not_change_core_runtime(monkeypatch):
    store = FakeStore()
    core = Core(
        raw_observation_store=store,
        evidence_store=store,
        report_store=store,
        finding_store=store,
        execution_failure_store=store,
        llm_manager=FakeLLMManager(),
        rules=(),
        progress_reporter=FailingRuntimeProgressReporter(),
    )

    def fake_execute(self, task):
        return {"plugin_id": task.plugin_id}

    from centaurus.plugin_manager.plugin_manager import PluginManager

    monkeypatch.setattr(PluginManager, "execute", fake_execute)

    investigation = Investigation(
        target="example.com",
        target_type="DOMAIN",
        intent="public_exposure_assessment",
    )

    result = core.run_investigation(investigation)

    assert result["status"] == "completed"
    assert investigation.status.value == "completed"
