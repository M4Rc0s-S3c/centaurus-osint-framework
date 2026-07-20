from centaurus.executor.execution.execution_task import ExecutionTask
from centaurus.plugin_manager.plugin_manager import PluginManager


def test_plugin_manager_creation():
    """
    Plugin Manager can be created.
    """

    manager = PluginManager()

    assert manager is not None


def test_plugin_manager_class_exists():
    """
    Plugin Manager exposes its public class.
    """

    assert PluginManager is not None

def test_plugin_manager_has_execute_method():
    """
    Plugin Manager exposes the execute method.
    """

    manager = PluginManager()

    assert hasattr(manager, "execute")


def test_plugin_manager_accepts_execution_task():
    """
    Plugin Manager accepts an ExecutionTask.
    """

    manager = PluginManager()

    task = ExecutionTask(plugin_id="whois")

    assert manager.execute(task) is None


