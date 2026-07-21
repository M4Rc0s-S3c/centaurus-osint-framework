from types import ModuleType

from centaurus.plugin_manager.plugin_manager import PluginManager


def test_load_plugin_method_exists():
    """
    Plugin Manager exposes the internal load method.
    """

    manager = PluginManager()

    assert hasattr(manager, "_load_plugin")


def test_load_plugin_returns_module():
    """
    Loading a valid plugin returns its module.
    """

    manager = PluginManager()

    module = manager._load_plugin("whois")

    assert isinstance(module, ModuleType)