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

    def __init__(self, core) -> None:
        """
        Create a new CLI instance.

        Args:
            core: Core framework instance.
        """

        self._core = core
        self._running = False

    def start(self) -> None:
        """
        Start the CLI interface.
        """

        self._running = True

    def stop(self) -> None:
        """
        Stop the CLI interface.
        """

        self._running = False
