"""
Plugin Manager component.

The Plugin Manager is responsible for discovering,
loading and managing framework plugins.
"""

from centaurus.executor.execution.execution_task import ExecutionTask

class PluginManager:
    """
    Manage the lifecycle of framework plugins.

    The Plugin Manager is the only component allowed
    to discover, validate, load and invoke plugins.
    """

    def __init__(self) -> None:
        """
        Create a new Plugin Manager instance.
        """

        pass

    # ==========================================================
    # Public interface
    # ==========================================================

    def execute(self, task: ExecutionTask) -> None:
        """
        Execute a single execution task.
        """

        pass   
    