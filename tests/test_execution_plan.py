from centaurus.executor.execution import (
    ExecutionPlan,
    ExecutionTask,
)


def test_execution_plan_can_be_created() -> None:
    """
    An ExecutionPlan can be instantiated.
    """

    plan = ExecutionPlan()

    assert isinstance(plan, ExecutionPlan)


def test_execution_task_can_be_created() -> None:
    """
    An ExecutionTask can be instantiated.
    """

    task = ExecutionTask(plugin_id="whois")

    assert isinstance(task, ExecutionTask)


def test_execution_plan_default_values() -> None:
    """
    ExecutionPlan starts with the expected default values.
    """

    plan = ExecutionPlan()

    assert plan.objective is None
    assert plan.tasks == []
    assert plan.metadata == {}


def test_execution_task_default_values() -> None:
    """
    ExecutionTask starts with the expected default values.
    """

    task = ExecutionTask(plugin_id="whois")

    assert task.plugin_id == "whois"
    assert task.parameters == {}
