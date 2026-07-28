from centaurus.executor.executor import Executor
from centaurus.executor.execution import (
    ExecutionPlan,
    ExecutionTask,
)


class FakePluginManager:
    """
    Test double for the Plugin Manager.
    """

    def __init__(self) -> None:
        """
        Create an empty fake Plugin Manager.
        """

        self.executed_tasks = []

    def execute(self, task: ExecutionTask) -> None:
        """
        Record the task received from the Executor.
        """

        self.executed_tasks.append(task)


def test_executor_creation():
    """
    Executor can be created with a Plugin Manager.
    """

    plugin_manager = FakePluginManager()

    executor = Executor(
        plugin_manager=plugin_manager,
    )

    assert executor is not None


def test_executor_has_execute_method():
    """
    Executor exposes the execute method.
    """

    plugin_manager = FakePluginManager()

    executor = Executor(
        plugin_manager=plugin_manager,
    )

    assert hasattr(executor, "execute")


def test_executor_accepts_execution_plan():
    """
    Executor accepts an ExecutionPlan.
    """

    plugin_manager = FakePluginManager()

    executor = Executor(
        plugin_manager=plugin_manager,
    )

    plan = ExecutionPlan()

    executor.execute(plan)


def test_executor_executes_empty_plan():
    """
    Executor can execute an empty ExecutionPlan.
    """

    plugin_manager = FakePluginManager()

    executor = Executor(
        plugin_manager=plugin_manager,
    )

    plan = ExecutionPlan()

    executor.execute(plan)

    assert plugin_manager.executed_tasks == []


def test_executor_executes_plan_with_tasks():
    """
    Executor delegates every task in the plan
    to the Plugin Manager.
    """

    plugin_manager = FakePluginManager()

    executor = Executor(
        plugin_manager=plugin_manager,
    )

    plan = ExecutionPlan()

    first_task = ExecutionTask(
        plugin_id="whois",
    )

    second_task = ExecutionTask(
        plugin_id="whois",
    )

    plan.tasks.append(first_task)
    plan.tasks.append(second_task)

    executor.execute(plan)

    assert plugin_manager.executed_tasks == [
        first_task,
        second_task,
    ]
