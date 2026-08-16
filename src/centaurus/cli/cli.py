"""
CLI interface component.

The CLI is responsible for user interaction
and communicates with the Core framework.
"""


class CLI:
    """
    Main command-line interface component.

    The CLI does not create or manage other
    framework components. It only communicates
    with the Core.
    """

    def __init__(self, core, request_interpreter=None) -> None:
        """
        Create a new CLI instance.

        Args:
            core: Core framework instance.
        """

        self._core = core
        self._request_interpreter = request_interpreter
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

        request = self._request_interpreter.interpret(user_input)
        return self._core.submit_request(request)

    def stop(self) -> None:
        """
        Stop the CLI interface.
        """

        self._running = False
