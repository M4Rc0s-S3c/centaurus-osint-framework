"""Final command-line application for the CENTAURUS distribution."""

from __future__ import annotations

from typing import Protocol

import typer
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from centaurus.cli.cli import CLI
from centaurus.core.core import Core
from centaurus.llm.exceptions import LLMError
from centaurus.llm.request_interpreter import RequestInterpreter
from centaurus.rules.catalog import DEFAULT_RULES


EXIT_OK = 0
EXIT_INTERNAL_ERROR = 1
EXIT_INVALID_REQUEST = 2
EXIT_OPERATIONAL_FAILURE = 3

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="CENTAURUS OSINT Framework command-line interface.",
)


class PromptSessionLike(Protocol):
    """Minimal prompt interface used by the conversational shell."""

    def prompt(self, message: str) -> str:
        """Read one line from the analyst."""


def build_runtime() -> tuple[CLI, Core]:
    """Compose the application boundary without moving domain logic into the CLI."""

    core = Core(rules=DEFAULT_RULES)
    interpreter = RequestInterpreter()
    cli = CLI(core, request_interpreter=interpreter)
    return cli, core


def _render_failures(core: Core, console: Console) -> None:
    failures = core.last_execution_failures
    if not failures:
        return

    table = Table(title="Tool execution failures", show_lines=True)
    table.add_column("Task", justify="right")
    table.add_column("Plugin")
    table.add_column("Category")
    table.add_column("Message")

    for failure in failures:
        table.add_row(
            str(failure.task_index),
            failure.plugin_id,
            getattr(failure.category, "value", str(failure.category)),
            failure.message,
        )

    console.print(table)


def _render_investigation(
    core: Core,
    investigation,
    console: Console,
) -> int:
    execution_status = core.last_execution_status
    domain_status = investigation.status.value

    if execution_status == "partial":
        visible_status = "PARTIAL — completed with reduced tool coverage"
    elif execution_status == "failed" or domain_status == "failed":
        visible_status = "FAILED"
    else:
        visible_status = domain_status.upper()

    summary = Table(show_header=False, box=None)
    summary.add_row("Investigation", investigation.id)
    summary.add_row("Target", f"{investigation.target_type}:{investigation.target}")
    summary.add_row("Intent", investigation.intent)
    summary.add_row("Status", visible_status)
    summary.add_row("Evidence", str(len(investigation.evidences)))
    summary.add_row("Findings", str(len(investigation.findings)))

    console.print(Panel(summary, title="CENTAURUS investigation"))
    _render_failures(core, console)

    if domain_status == "failed":
        console.print(
            "[red]The investigation did not produce a final Report.[/red]"
        )
        return EXIT_OPERATIONAL_FAILURE

    report = investigation.report
    if report is not None:
        findings = Table(title="Findings", show_lines=True)
        findings.add_column("Rule", no_wrap=True)
        findings.add_column("Conclusion")

        if report.findings:
            for finding in report.findings:
                findings.add_row(
                    finding.rule.id,
                    Text(finding.conclusion),
                )
        else:
            findings.add_row("—", Text("No Findings were produced."))

        console.print(findings)

    presentation = core.last_llm_output
    if presentation:
        console.print(
            Panel(
                Text(presentation),
                title="LLM presentation",
            )
        )
    elif report is not None:
        console.print(
            "[dim]LLM presentation unavailable; the deterministic Report "
            "remains the authoritative persisted result.[/dim]"
        )

    return EXIT_OK


def execute_request(
    cli: CLI,
    core: Core,
    user_input: str,
    console: Console,
) -> int:
    """Execute one natural-language request and present its result."""

    try:
        investigation = cli.submit(user_input)
    except ValueError as exc:
        console.print(f"[red]Invalid request:[/red] {exc}")
        return EXIT_INVALID_REQUEST
    except LLMError as exc:
        console.print(f"[red]LLM service error:[/red] {exc}")
        return EXIT_OPERATIONAL_FAILURE
    except Exception as exc:  # final user-facing boundary
        console.print(f"[red]CENTAURUS execution error:[/red] {exc}")
        return EXIT_INTERNAL_ERROR

    return _render_investigation(core, investigation, console)


def run_shell(
    cli: CLI,
    core: Core,
    console: Console,
    session: PromptSessionLike | None = None,
) -> int:
    """Run the minimal conversational shell required by the distribution."""

    prompt_session = session or PromptSession(history=InMemoryHistory())
    cli.start()

    console.print(
        Panel(
            "Enter a natural-language investigation request. "
            "Use /help for shell commands and /exit to leave.",
            title="CENTAURUS",
        )
    )

    try:
        while True:
            try:
                user_input = prompt_session.prompt("centaurus> ")
            except EOFError:
                break
            except KeyboardInterrupt:
                console.print()
                continue

            text = user_input.strip()
            if not text:
                continue

            command = text.lower()
            if command in {"/exit", "/quit", "exit", "quit"}:
                break
            if command in {"/help", "help", "?"}:
                console.print(
                    "[bold]/exit[/bold] leave the shell · "
                    "[bold]/help[/bold] show this message · "
                    "all other input is interpreted as an investigation request"
                )
                continue

            execute_request(cli, core, text, console)
    finally:
        cli.stop()

    return EXIT_OK


@app.command("investigate")
def investigate_command(
    request: list[str] = typer.Argument(
        ...,
        help="Natural-language investigation request.",
    ),
) -> None:
    """Run one investigation and print its structured result."""

    console = Console()
    cli, core = build_runtime()
    exit_code = execute_request(cli, core, " ".join(request), console)
    if exit_code != EXIT_OK:
        raise typer.Exit(code=exit_code)


@app.command("shell")
def shell_command() -> None:
    """Start the conversational Prompt Toolkit shell."""

    console = Console()
    cli, core = build_runtime()
    exit_code = run_shell(cli, core, console)
    if exit_code != EXIT_OK:
        raise typer.Exit(code=exit_code)
