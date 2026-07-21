"""
Plugin Manager component.

The Plugin Manager is responsible for discovering,
loading and managing framework plugins.
"""

from pathlib import Path

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
    
    # ==========================================================
    # Internal helpers
    # ==========================================================

    def _plugins_directory(self) -> Path:
        """
        Return the plugins directory.
        """

        return Path(__file__).resolve().parent.parent / "plugins"
    
    def _discover_plugins(self) -> list[str]:
        """
        Discover plugin packages available in the plugins directory.
        """

        plugins_path = self._plugins_directory()

        if not plugins_path.exists():
            return []

        return [
            entry.name
            for entry in plugins_path.iterdir()
            if entry.is_dir()
        ]
    
    def _validate_plugin(self, plugin_name: str) -> bool:
        """
        Validate the structure of a plugin package.
        """

        plugin_path = self._plugins_directory() / plugin_name

        if not plugin_path.is_dir():
            return False

        return (plugin_path / "__init__.py").is_file()
    
    
    