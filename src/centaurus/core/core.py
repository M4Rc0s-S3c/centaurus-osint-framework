"""
Core framework lifecycle manager.

The Core is responsible for creating, initializing and coordinating
all high-level framework components.
"""


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
        
    def initialize(self) -> None:
        """
        Initialize the framework.
        """

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
        