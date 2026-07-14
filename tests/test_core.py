from centaurus.core.core import Core


def test_core_initial_state():
    """
    Verify Core initial state.
    """

    core = Core()

    assert core._initialized is False
    assert core._running is False
   

def test_core_run_starts_framework():
    """
    Verify run initializes the framework.
    """

    core = Core()

    core.run()

    assert core._initialized is True
    assert core._running is True


def test_core_shutdown():
    """
    Verify framework shutdown.
    """

    core = Core()

    core.run()
    core.shutdown()

    assert core._running is False
    