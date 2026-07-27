from centaurus.plugins.base_plugin import BasePlugin


def test_base_plugin_class_exists():
    """
    BasePlugin exposes its public class.
    """

    assert BasePlugin is not None


def test_base_plugin_has_execute_method():
    """
    BasePlugin exposes the execute method.
    """

    assert hasattr(BasePlugin, "execute")


def test_base_plugin_is_abstract():
    """
    BasePlugin cannot be instantiated directly.
    """

    try:
        BasePlugin()

        assert False

    except TypeError:
        assert True
    
