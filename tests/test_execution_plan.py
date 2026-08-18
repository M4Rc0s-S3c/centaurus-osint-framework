from centaurus.executor.execution import (
    ExecutionPlan,
    ExecutionTask,
)


def test_execution_plan_can_be_created() -> None:
    """
    An ExecutionPlan can be instantiated for an Investigation.
    """

    plan = ExecutionPlan(
        investigation_id="INV-001",
    )

    assert isinstance(
        plan,
        ExecutionPlan,
    )


def test_execution_task_can_be_created() -> None:
    """
    An ExecutionTask can be instantiated.
    """

    task = ExecutionTask(
        plugin_id="whois",
    )

    assert isinstance(
        task,
        ExecutionTask,
    )


def test_execution_plan_stores_investigation_id() -> None:
    """
    ExecutionPlan stores the identifier of the Investigation
    that originated it.
    """

    plan = ExecutionPlan(
        investigation_id="INV-001",
    )

    assert plan.investigation_id == "INV-001"


def test_execution_plan_does_not_duplicate_investigation_objective() -> None:
    """ExecutionPlan contains operational context, not a domain objective copy."""

    plan = ExecutionPlan(investigation_id="INV-001")

    assert not hasattr(plan, "objective")


def test_execution_plan_default_values() -> None:
    """
    ExecutionPlan starts with the expected default values.
    """

    plan = ExecutionPlan(
        investigation_id="INV-001",
    )

    assert plan.investigation_id == "INV-001"
    assert plan.tasks == []
    assert plan.metadata == {}


def test_execution_task_default_values() -> None:
    """
    ExecutionTask starts with the expected default values.
    """

    task = ExecutionTask(
        plugin_id="whois",
    )

    assert task.plugin_id == "whois"
    assert task.parameters == {}