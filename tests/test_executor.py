from centaurus.executor.executor import Executor
from centaurus.executor.execution import (
    ExecutionPlan,
    ExecutionTask,
)


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


def test_executor_accepts_execution_plan():
    """
    Executor accepts an ExecutionPlan.
    """

    executor = Executor()

    plan = ExecutionPlan()

    executor.execute(plan)


def test_executor_executes_empty_plan():
    """
    Executor can execute an empty ExecutionPlan.
    """

    executor = Executor()

    plan = ExecutionPlan()

    executor.execute(plan)


def test_executor_executes_plan_with_tasks():
    """
    Executor can iterate over the tasks contained in an ExecutionPlan.
    """

    executor = Executor()

    plan = ExecutionPlan()

    plan.tasks.append(
        ExecutionTask(plugin_id="whois")
    )

    plan.tasks.append(
        ExecutionTask(plugin_id="whois")
    )

    executor.execute(plan)
