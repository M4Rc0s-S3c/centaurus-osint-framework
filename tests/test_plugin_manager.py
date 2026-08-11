from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from centaurus.evidence import EvidenceSource, RawObservation
from centaurus.executor.execution import ExecutionTask
from centaurus.plugin_manager.plugin_manager import PluginManager
from centaurus.plugins.base_plugin import BasePlugin


class ValidPlugin(BasePlugin):
    """
    Valid test plugin implementing the BasePlugin contract.
    """

    def __init__(self) -> None:
        """
        Create a valid test plugin.
        """

        self.received_parameters = None

    def execute(
        self,
        parameters: dict,
    ) -> RawObservation:
        """
        Execute the test plugin.
        """

        self.received_parameters = parameters

        return RawObservation(
            source=EvidenceSource.WHOIS,
            data={
                "value": "test",
            },
            collected_at=datetime.now(timezone.utc),
        )


class InvalidPlugin:
    """
    Invalid test plugin that does not inherit from BasePlugin.
    """

    def execute(
        self,
        parameters: dict,
    ) -> dict:
        """
        Execute the invalid test plugin.
        """

        return {}


def test_plugin_manager_creation() -> None:
    """
    Plugin Manager can be created.
    """

    manager = PluginManager()

    assert manager is not None


def test_plugin_manager_class_exists() -> None:
    """
    Plugin Manager exposes its public class.
    """

    assert PluginManager is not None


def test_plugin_manager_has_execute_method() -> None:
    """
    Plugin Manager exposes the execute method.
    """

    manager = PluginManager()

    assert hasattr(manager, "execute")


def test_plugin_manager_returns_plugin_result() -> None:
    """
    Plugin Manager returns the result produced by a plugin.
    """

    manager = PluginManager()

    task = ExecutionTask(
        plugin_id="whois",
        parameters={
            "domain": "example.com",
        },
    )

    result = manager.execute(task)

    assert isinstance(result, RawObservation)
    assert result.source == EvidenceSource.WHOIS
    assert isinstance(result.data, dict)


def test_plugin_manager_passes_task_parameters_to_plugin(
    monkeypatch,
) -> None:
    """
    Plugin Manager passes task parameters to the plugin.
    """

    manager = PluginManager()

    plugin = ValidPlugin()

    monkeypatch.setattr(
        manager,
        "_load_plugin_class",
        lambda plugin_name: lambda: plugin,
    )

    parameters = {
        "domain": "example.com",
    }

    task = ExecutionTask(
        plugin_id="test_plugin",
        parameters=parameters,
    )

    result = manager.execute(task)

    assert plugin.received_parameters == parameters

    assert isinstance(result, RawObservation)
    assert result.source == EvidenceSource.WHOIS
    assert result.data == {
        "value": "test",
    }


def test_load_plugin_class_returns_valid_plugin_class(
    monkeypatch,
) -> None:
    """
    Plugin Manager returns a Plugin class that implements BasePlugin.
    """

    manager = PluginManager()

    module = SimpleNamespace(
        Plugin=ValidPlugin,
    )

    monkeypatch.setattr(
        manager,
        "_load_plugin",
        lambda plugin_name: module,
    )

    plugin_class = manager._load_plugin_class(
        "test_plugin"
    )

    assert plugin_class is ValidPlugin

    assert issubclass(
        plugin_class,
        BasePlugin,
    )


def test_load_plugin_class_rejects_missing_plugin_class(
    monkeypatch,
) -> None:
    """
    Plugin Manager rejects a module without a Plugin class.
    """

    manager = PluginManager()

    module = SimpleNamespace()

    monkeypatch.setattr(
        manager,
        "_load_plugin",
        lambda plugin_name: module,
    )

    with pytest.raises(
        ValueError,
        match="does not expose a Plugin class",
    ):
        manager._load_plugin_class(
            "invalid_plugin"
        )


def test_load_plugin_class_rejects_non_class_plugin(
    monkeypatch,
) -> None:
    """
    Plugin Manager rejects a Plugin attribute that is not a class.
    """

    manager = PluginManager()

    module = SimpleNamespace(
        Plugin=ValidPlugin(),
    )

    monkeypatch.setattr(
        manager,
        "_load_plugin",
        lambda plugin_name: module,
    )

    with pytest.raises(
        TypeError,
        match="must be a class",
    ):
        manager._load_plugin_class(
            "invalid_plugin"
        )


def test_load_plugin_class_rejects_invalid_plugin_contract(
    monkeypatch,
) -> None:
    """
    Plugin Manager rejects a Plugin class that does not
    inherit from BasePlugin.
    """

    manager = PluginManager()

    module = SimpleNamespace(
        Plugin=InvalidPlugin,
    )

    monkeypatch.setattr(
        manager,
        "_load_plugin",
        lambda plugin_name: module,
    )

    with pytest.raises(
        TypeError,
        match="must inherit from BasePlugin",
    ):
        manager._load_plugin_class(
            "invalid_plugin"
        )