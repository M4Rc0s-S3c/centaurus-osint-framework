from centaurus.plugin_manager.plugin_manager import PluginManager


def test_validate_plugin_method_exists():
    """
    Plugin Manager exposes the internal validation method.
    """

    manager = PluginManager()

    assert hasattr(manager, "_validate_plugin")


def test_validate_plugin_returns_boolean():
    """
    Plugin validation returns a boolean value.
    """

    manager = PluginManager()

    result = manager._validate_plugin("dummy")

    assert isinstance(result, bool)


def test_validate_plugin_returns_true_for_valid_plugin(tmp_path):
    """
    A plugin package with __init__.py is valid.
    """

    plugins_dir = tmp_path / "plugins"
    plugin_dir = plugins_dir / "plugin_ok"

    plugin_dir.mkdir(parents=True)
    (plugin_dir / "__init__.py").touch()
    (plugin_dir / "plugin.py").touch()

    manager = PluginManager()
    manager._plugins_directory = lambda: plugins_dir

    assert manager._validate_plugin("plugin_ok") is True


def test_validate_plugin_returns_false_without_init_file(tmp_path):
    """
    A plugin package without __init__.py is not valid.
    """

    plugins_dir = tmp_path / "plugins"
    plugin_dir = plugins_dir / "plugin_invalid"

    plugin_dir.mkdir(parents=True)

    manager = PluginManager()
    manager._plugins_directory = lambda: plugins_dir

    assert manager._validate_plugin("plugin_invalid") is False


def test_validate_plugin_returns_false_when_directory_does_not_exist(tmp_path):
    """
    A non-existent plugin package is not valid.
    """

    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()

    manager = PluginManager()
    manager._plugins_directory = lambda: plugins_dir

    assert manager._validate_plugin("unknown_plugin") is False

