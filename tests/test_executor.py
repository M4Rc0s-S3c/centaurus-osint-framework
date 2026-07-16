from centaurus.executor.executor import Executor


def test_executor_creation():
    """
    Executor can be created.
    """

    executor = Executor()

    assert executor is not None


def test_executor_has_execute_method():
    """
    Executor exposes the execute method.
    """

    executor = Executor()

    assert hasattr(executor, "execute")
    