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


def test_cli_submit_interprets_and_forwards_structured_request():
    from centaurus.request import PUBLIC_EXPOSURE_ASSESSMENT, StructuredRequest

    expected_request = StructuredRequest(
        target="example.com",
        target_type="DOMAIN",
        intent=PUBLIC_EXPOSURE_ASSESSMENT,
    )

    class FakeInterpreter:
        def __init__(self):
            self.received = []

        def interpret(self, text):
            self.received.append(text)
            return expected_request

    class FakeCore:
        def __init__(self):
            self.received = []

        def submit_request(self, request, *, analyst_question=None):
            self.received.append((request, analyst_question))
            return "investigation"

    core = FakeCore()
    interpreter = FakeInterpreter()
    cli = CLI(core, request_interpreter=interpreter)

    result = cli.submit("Investiga example.com")

    assert result == "investigation"
    assert interpreter.received == ["Investiga example.com"]
    assert core.received == [
        (expected_request, "Investiga example.com"),
    ]


def test_cli_submit_requires_configured_interpreter():
    cli = CLI(Core())

    try:
        cli.submit("Investiga example.com")
    except RuntimeError as exc:
        assert "interpreter" in str(exc)
    else:
        raise AssertionError("CLI.submit() should require an interpreter")
