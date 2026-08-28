"""Final command-line application for the CENTAURUS distribution."""

from __future__ import annotations

import logging
from dataclasses import replace
from importlib.metadata import PackageNotFoundError, version
from typing import Protocol

import typer
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from centaurus.capabilities import (
    DEFERRED_TARGET_CAPABILITIES,
    IMPLEMENTED_TOOLS,
    OPERATIONAL_TARGET_CAPABILITIES,
    PUBLIC_EXPOSURE_ASSESSMENT,
)
from centaurus.cli.cli import CLI
from centaurus.cli.progress import RichRuntimeProgressReporter
from centaurus.config import RuntimeConfigurationError, RuntimeSettings
from centaurus.core.core import Core
from centaurus.llm import (
    ANALYST_ASSISTANCE_INFERENCE_PROFILE,
    LLMManager,
    OllamaProvider,
)
from centaurus.llm.exceptions import LLMError
from centaurus.llm.ollama_intent_provider import OllamaIntentProvider
from centaurus.llm.request_interpreter import RequestInterpreter
from centaurus.observability import RuntimeProgressReporter, configure_logging
from centaurus.persistence.filesystem.evidence_store import FilesystemEvidenceStore
from centaurus.persistence.filesystem.execution_failure_store import (
    FilesystemExecutionFailureStore,
)
from centaurus.persistence.filesystem.finding_store import FilesystemFindingStore
from centaurus.persistence.filesystem.raw_observation_store import (
    FilesystemRawObservationStore,
)
from centaurus.persistence.filesystem.report_store import FilesystemReportStore
from centaurus.rules.catalog import DEFAULT_RULES


EXIT_OK = 0
EXIT_INTERNAL_ERROR = 1
EXIT_INVALID_REQUEST = 2
EXIT_OPERATIONAL_FAILURE = 3

logger = logging.getLogger(__name__)

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help=(
        "CENTAURUS assesses public exposure of supported targets using OSINT "
        "collection and deterministic Rules. Use 'capabilities' to discover "
        "the current distribution before starting an investigation."
    ),
)


def _distribution_version() -> str:
    """Return the installed distribution version without building runtime state."""

    try:
        return version("centaurus")
    except PackageNotFoundError:
        return "development"


def render_capabilities(console: Console, *, show_rules: bool = False) -> None:
    """Render static distribution capabilities without initializing the runtime."""

    console.print(
        Panel(
            "Assess public exposure using deterministic OSINT collection and Rules. "
            "Capabilities are static distribution metadata and require no Ollama "
            "connection.",
            title="CENTAURUS capabilities",
        )
    )

    intent_table = Table(title="Supported Intent")
    intent_table.add_column("Intent")
    intent_table.add_column("Purpose")
    intent_table.add_row(
        PUBLIC_EXPOSURE_ASSESSMENT,
        "Assess publicly observable exposure for operational target types.",
    )
    console.print(intent_table)

    target_table = Table(title="Target coverage", show_lines=True)
    target_table.add_column("Target")
    target_table.add_column("Status")
    target_table.add_column("Tasks", justify="right")
    target_table.add_column("Tools")
    target_table.add_column("Scope")

    for capability in OPERATIONAL_TARGET_CAPABILITIES:
        target_table.add_row(
            capability.target_type,
            capability.status,
            str(len(capability.tasks)),
            ", ".join(capability.tools),
            capability.description,
        )
    for capability in DEFERRED_TARGET_CAPABILITIES:
        target_table.add_row(
            capability.target_type,
            capability.status,
            "0",
            "—",
            capability.description,
        )
    console.print(target_table)

    console.print(
        "[bold]Implemented tools:[/bold] " + ", ".join(IMPLEMENTED_TOOLS)
    )
    console.print(
        f"[bold]Productive deterministic Rules:[/bold] {len(DEFAULT_RULES)}"
    )
    console.print(
        "[bold]Output:[/bold] report.json (authoritative), report.md "
        "(deterministic projection), LLM analyst assistance (ephemeral)"
    )

    if not show_rules:
        console.print(
            "[dim]Use 'centaurus capabilities --rules' to list productive Rules.[/dim]"
        )
        return

    render_rules(console)


def render_rules(console: Console) -> None:
    """Render the productive deterministic Rule catalog offline."""

    rules_table = Table(title="Productive Rules", show_lines=True)
    rules_table.add_column("Rule", no_wrap=True)
    rules_table.add_column("Category")
    rules_table.add_column("Name")
    rules_table.add_column("Description")
    for rule in DEFAULT_RULES:
        rules_table.add_row(rule.id, rule.category, rule.name, rule.description)
    console.print(rules_table)


@app.callback(invoke_without_command=True)
def application_callback(
    show_version: bool = typer.Option(
        False,
        "--version",
        is_eager=True,
        help="Show the installed CENTAURUS version and exit.",
    ),
) -> None:
    """CENTAURUS distribution entrypoint."""

    if show_version:
        typer.echo(f"CENTAURUS {_distribution_version()}")
        raise typer.Exit(code=EXIT_OK)


@app.command("capabilities")
def capabilities_command(
    rules: bool = typer.Option(
        False,
        "--rules",
        help="Include the productive deterministic Rule catalog.",
    ),
) -> None:
    """Show supported targets, Intent, tools and optional Rules offline."""

    render_capabilities(Console(), show_rules=rules)


@app.command("rules")
def rules_command() -> None:
    """Show the productive deterministic Rule catalog offline."""

    render_rules(Console())


class PromptSessionLike(Protocol):
    """Minimal prompt interface used by the conversational shell."""

    def prompt(self, message: str) -> str:
        """Read one line from the analyst."""


def build_runtime(
    settings: RuntimeSettings | None = None,
    progress_reporter: RuntimeProgressReporter | None = None,
) -> tuple[CLI, Core]:
    """Compose the product runtime from validated external configuration."""

    runtime = settings or RuntimeSettings.from_env()
    configure_logging(runtime)

    core = Core(
        raw_observation_store=FilesystemRawObservationStore(runtime.workspace),
        evidence_store=FilesystemEvidenceStore(runtime.workspace),
        report_store=FilesystemReportStore(runtime.workspace),
        finding_store=FilesystemFindingStore(runtime.workspace),
        execution_failure_store=FilesystemExecutionFailureStore(runtime.workspace),
        llm_manager=LLMManager(
            provider=OllamaProvider(
                base_url=runtime.ollama_base_url,
                model=runtime.ollama_model,
                timeout=runtime.ollama_analyst_assistance_timeout,
                inference_profile=replace(
                    ANALYST_ASSISTANCE_INFERENCE_PROFILE,
                    num_ctx=runtime.ollama_analyst_assistance_num_ctx,
                    num_predict=runtime.ollama_analyst_assistance_num_predict,
                ),
            )
        ),
        rules=DEFAULT_RULES,
        progress_reporter=progress_reporter,
    )
    interpreter = RequestInterpreter(
        provider=OllamaIntentProvider(
            base_url=runtime.ollama_base_url,
            model=runtime.ollama_model,
            timeout=runtime.ollama_interpretation_timeout,
        )
    )
    cli = CLI(
        core,
        request_interpreter=interpreter,
        progress_reporter=progress_reporter,
    )

    logger.info(
        "runtime configured workspace=%s ollama_base_url=%s ollama_model=%s "
        "ollama_analyst_assistance_timeout=%s "
        "ollama_analyst_assistance_num_ctx=%s "
        "ollama_analyst_assistance_num_predict=%s log_level=%s",
        runtime.workspace,
        runtime.ollama_base_url,
        runtime.ollama_model,
        runtime.ollama_analyst_assistance_timeout,
        runtime.ollama_analyst_assistance_num_ctx,
        runtime.ollama_analyst_assistance_num_predict,
        runtime.log_level,
    )
    return cli, core


def _build_runtime_or_exit(console: Console) -> tuple[CLI, Core]:
    """Translate invalid deployment configuration at the CLI boundary."""

    try:
        return build_runtime(
            progress_reporter=RichRuntimeProgressReporter(console),
        )
    except RuntimeConfigurationError as exc:
        console.print(f"[red]CENTAURUS configuration error:[/red] {exc}")
        raise typer.Exit(code=EXIT_INTERNAL_ERROR) from exc


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
                title="LLM analyst assistance — ephemeral",
            )
        )
    elif report is not None:
        console.print(
            "[dim]LLM analyst assistance unavailable; the deterministic Report "
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
        logger.warning("request rejected: %s", exc)
        console.print(f"[red]Invalid request:[/red] {exc}")
        return EXIT_INVALID_REQUEST
    except LLMError as exc:
        logger.warning("LLM service error before investigation completion: %s", exc)
        console.print(f"[red]LLM service error:[/red] {exc}")
        return EXIT_OPERATIONAL_FAILURE
    except Exception as exc:  # final user-facing boundary
        logger.exception("unexpected error at CLI execution boundary")
        console.print(f"[red]CENTAURUS execution error:[/red] {exc}")
        return EXIT_INTERNAL_ERROR

    logger.info(
        "investigation finished id=%s domain_status=%s execution_status=%s "
        "evidence=%d findings=%d failures=%d",
        investigation.id,
        investigation.status.value,
        core.last_execution_status,
        len(investigation.evidences),
        len(investigation.findings),
        len(core.last_execution_failures),
    )
    return _render_investigation(core, investigation, console)


def _shell_meta_command(text: str) -> tuple[str, bool] | None:
    """Parse deterministic shell-only discovery commands.

    The optional ``centaurus`` prefix is accepted so an analyst can use the
    same vocabulary inside the conversational shell without leaving it.
    """

    normalized = text.strip().lower()
    if normalized.startswith("/"):
        normalized = normalized[1:].lstrip()

    tokens = normalized.split()
    if tokens and tokens[0] == "centaurus":
        tokens = tokens[1:]

    if tokens == ["capabilities"]:
        return ("capabilities", False)
    if tokens == ["rules"]:
        return ("rules", True)
    if tokens in (
        ["capabilities", "--rules"],
        ["capabilities", "rules"],
        ["rules", "capabilities"],
    ):
        return ("capabilities", True)

    return None


def run_shell(
    cli: CLI,
    core: Core,
    console: Console,
    session: PromptSessionLike | None = None,
) -> int:
    """Run the minimal conversational shell required by the distribution."""

    prompt_session = session or PromptSession(history=InMemoryHistory())
    cli.start()
    logger.info("interactive shell started")

    console.print(
        Panel(
            "Assess public exposure with a natural-language request. "
            "Use /capabilities to see supported targets, tools and Rules; "
            "use /help for shell commands and /exit to leave.",
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
                    "[bold]/capabilities[/bold] show supported targets and tools · "
                    "[bold]/rules[/bold] show productive Rules · "
                    "[bold]/capabilities --rules[/bold] show both · "
                    "the optional [bold]centaurus[/bold] prefix is accepted · "
                    "[bold]/exit[/bold] leave the shell · "
                    "[bold]/help[/bold] show this message · "
                    "all other input is interpreted as an investigation request"
                )
                continue

            meta_command = _shell_meta_command(text)
            if meta_command is not None:
                name, show_rules = meta_command
                if name == "rules":
                    render_rules(console)
                else:
                    render_capabilities(console, show_rules=show_rules)
                continue

            execute_request(cli, core, text, console)
    finally:
        cli.stop()
        logger.info("interactive shell stopped")

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
    cli, core = _build_runtime_or_exit(console)
    exit_code = execute_request(cli, core, " ".join(request), console)
    if exit_code != EXIT_OK:
        raise typer.Exit(code=exit_code)


@app.command("shell")
def shell_command() -> None:
    """Start the conversational Prompt Toolkit shell."""

    console = Console()
    cli, core = _build_runtime_or_exit(console)
    exit_code = run_shell(cli, core, console)
    if exit_code != EXIT_OK:
        raise typer.Exit(code=exit_code)
