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

