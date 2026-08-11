"""
Plugin Manager component.

The Plugin Manager is responsible for discovering,
validating, loading and executing framework plugins.
"""

import importlib
from pathlib import Path

from centaurus.evidence.raw_observation import RawObservation
from centaurus.executor.execution import ExecutionTask
from centaurus.plugins.base_plugin import BasePlugin


class PluginManager:
    """
    Plugin Manager component.

    The Plugin Manager is the only component allowed
    to discover, validate, load and invoke plugins.
    """

    # ==========================================================
    # Public interface
    # ==========================================================

    def execute(
        self,
        task: ExecutionTask,
    ) -> RawObservation:
        """
        Execute a single execution task.

        The Plugin Manager loads the plugin requested by the task,
        verifies that its public Plugin class implements the
        BasePlugin contract, creates an instance, executes it and
        returns the RawObservation produced by the plugin.
        """

        plugin_class = self._load_plugin_class(
        task.plugin_id,
        )

        plugin = plugin_class()

        return plugin.execute(
        task.parameters,
        )

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

        return (
            (plugin_path / "__init__.py").is_file()
            and (plugin_path / "plugin.py").is_file()
        )

    def _load_plugin(self, plugin_name: str):
        """
        Load a validated plugin package.
        """

        if not self._validate_plugin(plugin_name):
            raise ValueError(
                f"Invalid plugin: {plugin_name}"
            )

        module_name = f"centaurus.plugins.{plugin_name}"

        return importlib.import_module(module_name)

    def _load_plugin_class(
        self,
        plugin_name: str,
    ) -> type[BasePlugin]:
        """
        Load and validate the public Plugin class.

        The plugin package must expose a class named Plugin
        that inherits from BasePlugin.
        """

        module = self._load_plugin(plugin_name)

        plugin_class = getattr(
            module,
            "Plugin",
            None,
        )

        if plugin_class is None:
            raise ValueError(
                f"Plugin '{plugin_name}' does not expose "
                "a Plugin class"
            )

        if not isinstance(plugin_class, type):
            raise TypeError(
                f"Plugin '{plugin_name}'.Plugin "
                "must be a class"
            )

        if not issubclass(plugin_class, BasePlugin):
            raise TypeError(
                f"Plugin '{plugin_name}'.Plugin "
                "must inherit from BasePlugin"
            )

        return plugin_class
    