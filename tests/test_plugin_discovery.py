from centaurus.plugin_manager.plugin_manager import PluginManager


def test_discover_plugins_method_exists():
    """
    Plugin Manager exposes the internal discovery method.
    """

    manager = PluginManager()

    assert hasattr(manager, "_discover_plugins")


def test_discover_plugins_returns_list():
    """
    Plugin discovery returns a list.
    """

    manager = PluginManager()

    plugins = manager._discover_plugins()

    assert isinstance(plugins, list)


def test_discover_plugins_returns_plugin_names():
    """
    Plugin discovery returns plugin names.
    """

    manager = PluginManager()

    plugins = manager._discover_plugins()

    assert all(isinstance(plugin, str) for plugin in plugins)



