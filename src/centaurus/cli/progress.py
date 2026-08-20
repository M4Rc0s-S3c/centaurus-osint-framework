"""Rich adapter for ephemeral CENTAURUS runtime progress."""

from __future__ import annotations

from datetime import timedelta
from time import monotonic

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from centaurus.observability.progress import RuntimeProgressEvent


_TOOL_LABELS = {
    "whois": "WHOIS",
    "rdap": "RDAP",
    "dnsrecon": "DNSRecon",
    "sublist3r": "Sublist3r",
    "crtsh": "crt.sh",
    "theharvester": "TheHarvester",
}


class RichRuntimeProgressReporter:
    """Render live progress plus a compact persistent history in a TTY."""

    def __init__(self, console: Console) -> None:
        self._console = console
        self._enabled = console.is_terminal
        self._progress: Progress | None = None
        self._task_id: int | None = None
        self._started_at: float | None = None
        self._current_event: RuntimeProgressEvent | None = None

    def start(self) -> None:
        if not self._enabled or self._progress is not None:
            return

        self._started_at = monotonic()
        self._current_event = None
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("{task.description}"),
            TimeElapsedColumn(),
            console=self._console,
            transient=True,
            refresh_per_second=8,
        )
        self._progress.start()
        self._task_id = self._progress.add_task("Preparando...", total=None)

    def publish(self, event: RuntimeProgressEvent) -> None:
        if not self._enabled:
            return
        if self._progress is None:
            self.start()
        if self._progress is None or self._task_id is None:
            return

        if event.kind == "session_completed":
            self._persist_previous_phase()
            return
        if event.kind == "task_succeeded":
            self._print_success(event)
            self._current_event = None
        elif event.kind == "task_failed":
            self._print_failure(event)
            self._current_event = None
        else:
            self._persist_previous_phase()
            self._current_event = event

        self._progress.update(
            self._task_id,
            description=self._format_event(event),
        )
        self._progress.refresh()

    def stop(self) -> None:
        if self._progress is None:
            return

        self._progress.stop()
        self._progress = None
        self._task_id = None
        self._started_at = None
        self._current_event = None

    def _persist_previous_phase(self) -> None:
        event = self._current_event
        if event is None or event.kind != "phase":
            return
        self._print_success(event)
        self._current_event = None

    def _print_success(self, event: RuntimeProgressEvent) -> None:
        if self._progress is None:
            return
        self._progress.console.print(
            f"[green]✓[/green] {self._format_history_event(event)}"
            f" · [dim]{self._elapsed_label()}[/dim]"
        )

    def _print_failure(self, event: RuntimeProgressEvent) -> None:
        if self._progress is None:
            return
        self._progress.console.print(
            f"[yellow]![/yellow] {self._format_failure(event)}"
            f" · [dim]{self._elapsed_label()}[/dim]"
        )

    def _elapsed_label(self) -> str:
        if self._started_at is None:
            return "0:00:00"
        seconds = max(0, int(monotonic() - self._started_at))
        return str(timedelta(seconds=seconds))

    @staticmethod
    def _tool_label(event: RuntimeProgressEvent) -> str:
        label = _TOOL_LABELS.get(event.plugin_id or "", event.plugin_id or "tool")
        if event.plugin_id == "dnsrecon":
            if event.task_variant == "dmarc":
                return f"{label} · DMARC"
            return f"{label} · estándar"
        if event.task_variant:
            return f"{label} · {event.task_variant}"
        return label

    @classmethod
    def _format_event(cls, event: RuntimeProgressEvent) -> str:
        if event.task_index is None or event.task_total is None:
            return event.message

        tool = cls._tool_label(event)
        return f"{event.message} · {event.task_index}/{event.task_total} · {tool}"

    @classmethod
    def _format_history_event(cls, event: RuntimeProgressEvent) -> str:
        if event.task_index is None or event.task_total is None:
            return event.message

        tool = cls._tool_label(event)
        return f"{event.task_index}/{event.task_total} · {tool}"

    @classmethod
    def _format_failure(cls, event: RuntimeProgressEvent) -> str:
        tool = cls._tool_label(event)
        category = event.failure_category or "execution_error"
        position = ""
        if event.task_index is not None and event.task_total is not None:
            position = f"{event.task_index}/{event.task_total} · "
        return (
            f"{position}{tool} · {category} · "
            "continuando con cobertura parcial"
        )
