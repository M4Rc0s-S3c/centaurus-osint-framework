"""
Core framework lifecycle manager.

The Core is responsible for creating, initializing and coordinating
all high-level framework components.
"""

from centaurus.cli.cli import CLI

class Core:
    """
    Main lifecycle controller of the Centaurus framework.
    """

    def __init__(self) -> None:
        """
        Create a new Core instance.
        """

        self._initialized = False
        self._running = False

        self._cli = None

    # ==========================================================
    # Public interface
    # ==========================================================
        
    def initialize(self) -> None:
        """
        Initialize the framework.
        """

        self._create_components()

        self._initialized = True
      
    def run(self) -> None:
        """
        Start framework operation.
        """

        if not self._initialized:
            self.initialize()

        self._running = True

    def shutdown(self) -> None:
        """
        Stop framework operation.
        """

        self._running = False

    # ==========================================================
    # Internal implementation
    # ==========================================================
    def _create_components(self) -> None:
        """
        Create all framework components.

        Component creation is centralized in the Core in order to
        guarantee a deterministic framework lifecycle.
        """

        self._create_cli()

    def _create_cli(self) -> None:
        """
        Create the CLI component.
        """

        self._cli = CLI(self)
        
    