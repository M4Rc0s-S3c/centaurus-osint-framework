"""
CLI interface component.

The CLI is responsible for user interaction
and communicates with the Core framework.
"""

import logging

from centaurus.observability import (
    NullRuntimeProgressReporter,
    RuntimeProgressReporter,
    RuntimeProgressEvent,
)


logger = logging.getLogger("centaurus.cli")


class CLI:
    """
    Main command-line interface component.

    The CLI does not create or manage other
    framework components. It only communicates
    with the Core.
    """

    def __init__(
        self,
        core,
        request_interpreter=None,
        progress_reporter: RuntimeProgressReporter | None = None,
    ) -> None:
        """
        Create a new CLI instance.

        Args:
            core: Core framework instance.
        """

        self._core = core
        self._request_interpreter = request_interpreter
        self._progress_reporter = progress_reporter or NullRuntimeProgressReporter()
        self._running = False

    def start(self) -> None:
        """
        Start the CLI interface.
        """

        self._running = True

    def submit(self, user_input: str):
        """Interpret one user request and submit it to the Core."""

        if self._request_interpreter is None:
            raise RuntimeError("CLI request interpreter has not been configured")

        self._safe_progress("start")
        try:
            self._safe_progress(
                "publish",
                RuntimeProgressEvent(message="Interpretando la petición"),
            )
            request = self._request_interpreter.interpret(user_input)
            return self._core.submit_request(
                request,
                analyst_question=user_input.strip(),
            )
        finally:
            self._safe_progress("stop")

    def _safe_progress(self, method: str, *args) -> None:
        """Keep presentation failures from changing request/runtime semantics."""

        try:
            getattr(self._progress_reporter, method)(*args)
        except Exception:
            self._progress_reporter = NullRuntimeProgressReporter()
            logger.warning(
                "runtime progress reporter failed; request continues",
                exc_info=True,
            )

    def stop(self) -> None:
        """
        Stop the CLI interface.
        """

        self._running = False
