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
        self._components = {}

    def initialize(self) -> None:
        """
        Initialize the framework.
        """

        self._initialized = True
    
    def register_component(self, name: str, component: object) -> None:
        """
        Register a framework component.
        """

        self._components[name] = component

    def get_component(self, name: str) -> object | None:
        """
        Retrieve a registered component.
        """

        return self._components.get(name)

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
        