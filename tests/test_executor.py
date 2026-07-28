"""
Unit tests for the Executor component.
"""

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

    def execute(
        self,
        task: ExecutionTask,
    ) -> dict:
        """
        Record the received task and return a simulated result.
        """

        self.executed_tasks.append(task)

        return {
            "plugin_id": task.plugin_id,
            "status": "success",
            "data": task.parameters,
        }


def test_executor_creation() -> None:
    """
    Executor can be created with a Plugin Manager.
    """

    plugin_manager = FakePluginManager()

    executor = Executor(
        plugin_manager=plugin_manager,
    )

    assert executor is not None


def test_executor_has_execute_method() -> None:
    """
    Executor exposes the execute method.
    """

    plugin_manager = FakePluginManager()

    executor = Executor(
        plugin_manager=plugin_manager,
    )

    assert hasattr(executor, "execute")


def test_executor_accepts_execution_plan() -> None:
    """
    Executor accepts an ExecutionPlan.
    """

    plugin_manager = FakePluginManager()

    executor = Executor(
        plugin_manager=plugin_manager,
    )

    plan = ExecutionPlan()

    results = executor.execute(plan)

    assert results == []


def test_executor_executes_empty_plan() -> None:
    """
    Executor returns an empty result list for an empty plan.
    """

    plugin_manager = FakePluginManager()

    executor = Executor(
        plugin_manager=plugin_manager,
    )

    plan = ExecutionPlan()

    results = executor.execute(plan)

    assert plugin_manager.executed_tasks == []
    assert results == []


def test_executor_executes_plan_with_tasks() -> None:
    """
    Executor delegates every task in the plan to the Plugin
    Manager and returns the results in execution order.
    """

    plugin_manager = FakePluginManager()

    executor = Executor(
        plugin_manager=plugin_manager,
    )

    plan = ExecutionPlan()

    first_task = ExecutionTask(
        plugin_id="whois",
        parameters={
            "domain": "example.com",
        },
    )

    second_task = ExecutionTask(
        plugin_id="whois",
        parameters={
            "domain": "openai.com",
        },
    )

    plan.tasks.append(first_task)
    plan.tasks.append(second_task)

    results = executor.execute(plan)

    assert plugin_manager.executed_tasks == [
        first_task,
        second_task,
    ]

    assert results == [
        {
            "plugin_id": "whois",
            "status": "success",
            "data": {
                "domain": "example.com",
            },
        },
        {
            "plugin_id": "whois",
            "status": "success",
            "data": {
                "domain": "openai.com",
            },
        },
    ]