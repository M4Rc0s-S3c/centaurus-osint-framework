"""
Unit tests for the Executor component.
"""

from centaurus.executor.executor import Executor
from centaurus.executor.execution import (
    ExecutionFailureCategory,
    ExecutionPlan,
    ExecutionTask,
)
from centaurus.exceptions import PluginExecutionError


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

        self.executed_tasks.append(
            task,
        )

        return {
            "plugin_id": task.plugin_id,
            "status": "success",
            "data": task.parameters,
        }


class SelectiveFailingPluginManager(FakePluginManager):
    """Fail selected plugin IDs while recording sequential execution."""

    def __init__(self, failing_plugin_ids: set[str]) -> None:
        super().__init__()
        self._failing_plugin_ids = failing_plugin_ids

    def execute(
        self,
        task: ExecutionTask,
    ) -> dict:
        self.executed_tasks.append(task)

        if task.plugin_id in self._failing_plugin_ids:
            try:
                raise TimeoutError("tool timed out")
            except TimeoutError as exc:
                raise PluginExecutionError(
                    task.plugin_id,
                    "tool timed out",
                ) from exc

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

    assert hasattr(
        executor,
        "execute",
    )


def test_executor_accepts_execution_plan() -> None:
    """
    Executor accepts an ExecutionPlan.
    """

    plugin_manager = FakePluginManager()

    executor = Executor(
        plugin_manager=plugin_manager,
    )

    plan = ExecutionPlan(
        investigation_id="INV-TEST",
    )

    results = executor.execute(
        plan,
    )

    assert results == {
        "status": "completed",
        "results": [],
        "failures": [],
    }


def test_executor_executes_empty_plan() -> None:
    """
    Executor returns an empty execution report for an empty plan.
    """

    plugin_manager = FakePluginManager()

    executor = Executor(
        plugin_manager=plugin_manager,
    )

    plan = ExecutionPlan(
        investigation_id="INV-TEST",
    )

    results = executor.execute(
        plan,
    )

    assert plugin_manager.executed_tasks == []

    assert results == {
        "status": "completed",
        "results": [],
        "failures": [],
    }


def test_executor_executes_plan_with_tasks() -> None:
    """
    Executor delegates every task in the plan to the Plugin
    Manager and returns the execution report.
    """

    plugin_manager = FakePluginManager()

    executor = Executor(
        plugin_manager=plugin_manager,
    )

    plan = ExecutionPlan(
        investigation_id="INV-TEST",
    )

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

    plan.tasks.append(
        first_task,
    )

    plan.tasks.append(
        second_task,
    )

    results = executor.execute(
        plan,
    )

    assert plugin_manager.executed_tasks == [
        first_task,
        second_task,
    ]

    assert results == {
        "status": "completed",
        "results": [
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
        ],
        "failures": [],
    }


def test_executor_continues_after_one_plugin_failure() -> None:
    """A failed task does not prevent later planned tasks from running."""

    plugin_manager = SelectiveFailingPluginManager({"rdap_lookup"})
    executor = Executor(plugin_manager=plugin_manager)
    plan = ExecutionPlan(investigation_id="INV-TEST")

    first = ExecutionTask(plugin_id="whois_lookup", parameters={})
    second = ExecutionTask(plugin_id="rdap_lookup", parameters={})
    third = ExecutionTask(plugin_id="crtsh_lookup", parameters={})
    plan.tasks.extend((first, second, third))

    result = executor.execute(plan)

    assert plugin_manager.executed_tasks == [first, second, third]
    assert result["status"] == "partial"
    assert [item["plugin_id"] for item in result["results"]] == [
        "whois_lookup",
        "crtsh_lookup",
    ]
    assert len(result["failures"]) == 1
    assert result["failures"][0].task_index == 2
    assert result["failures"][0].category == ExecutionFailureCategory.TIMEOUT


def test_executor_marks_nonempty_plan_failed_when_every_task_fails() -> None:
    """A non-empty plan is failed when it produces no successful result."""

    plugin_manager = SelectiveFailingPluginManager({"whois", "rdap"})
    executor = Executor(plugin_manager=plugin_manager)
    plan = ExecutionPlan(investigation_id="INV-TEST")
    plan.tasks.extend(
        (
            ExecutionTask(plugin_id="whois", parameters={}),
            ExecutionTask(plugin_id="rdap", parameters={}),
        )
    )

    result = executor.execute(plan)

    assert result["status"] == "failed"
    assert result["results"] == []
    assert len(result["failures"]) == 2


def test_executor_keeps_sequential_task_indexes_across_failures() -> None:
    """Failure records identify the exact planned task position."""

    plugin_manager = SelectiveFailingPluginManager({"dnsrecon"})
    executor = Executor(plugin_manager=plugin_manager)
    plan = ExecutionPlan(investigation_id="INV-TEST")
    plan.tasks.extend(
        (
            ExecutionTask(plugin_id="whois", parameters={}),
            ExecutionTask(plugin_id="dnsrecon", parameters={"mode": "standard"}),
            ExecutionTask(plugin_id="dnsrecon", parameters={"mode": "dmarc"}),
        )
    )

    result = executor.execute(plan)

    assert result["status"] == "partial"
    assert [failure.task_index for failure in result["failures"]] == [2, 3]
    assert [failure.parameters for failure in result["failures"]] == [
        {"mode": "standard"},
        {"mode": "dmarc"},
    ]