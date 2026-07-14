from centaurus.cli.cli import CLI
from centaurus.core.core import Core


def test_cli_creation():
    """
    CLI can be created with a Core instance.
    """

    core = Core()
    cli = CLI(core)

    assert cli is not None


def test_cli_start():
    """
    CLI starts correctly.
    """

    core = Core()
    cli = CLI(core)

    cli.start()

    assert cli._running is True


def test_cli_stop():
    """
    CLI stops correctly.
    """

    core = Core()
    cli = CLI(core)

    cli.start()
    cli.stop()

    assert cli._running is False
    