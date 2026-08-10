from centaurus.planner.planner import Planner
from centaurus.executor.execution import (
    ExecutionPlan,
    ExecutionTask,
)
from centaurus.investigation import Investigation


def test_planner_creation():
    """
    Planner can be created.
    """

    planner = Planner()

    assert planner is not None


def test_planner_has_plan_method():
    """
    Planner exposes the public planning interface.
    """

    planner = Planner()

    assert hasattr(
        planner,
        "plan",
    )


def test_planner_returns_execution_plan():
    """
    Planner returns an ExecutionPlan instance.
    """

    planner = Planner()

    investigation = Investigation(
        objective="example.com",
    )

    plan = planner.plan(
        investigation,
    )

    assert isinstance(
        plan,
        ExecutionPlan,
    )


def test_planner_creates_execution_task():
    """
    Planner creates an execution plan containing one execution task.
    """

    planner = Planner()

    investigation = Investigation(
        objective="example.com",
    )

    plan = planner.plan(
        investigation,
    )

    assert isinstance(
        plan,
        ExecutionPlan,
    )

    assert len(plan.tasks) == 1

    assert isinstance(
        plan.tasks[0],
        ExecutionTask,
    )


def test_planner_associates_plan_with_investigation():
    """
    Planner associates the ExecutionPlan with the Investigation
    that originated it.
    """

    planner = Planner()

    investigation = Investigation(
        objective="example.com",
    )

    plan = planner.plan(
        investigation,
    )

    assert plan.investigation_id == investigation.id


def test_planner_copies_investigation_objective_to_plan():
    """
    Planner copies the Investigation objective into the
    ExecutionPlan.
    """

    planner = Planner()

    investigation = Investigation(
        objective="example.com",
    )

    plan = planner.plan(
        investigation,
    )

    assert plan.objective == "example.com"


def test_planner_passes_target_to_execution_task():
    """
    Planner copies the investigation objective into the
    ExecutionTask target parameter.
    """

    planner = Planner()

    investigation = Investigation(
        objective="example.com",
    )

    plan = planner.plan(
        investigation,
    )

    assert len(plan.tasks) == 1

    assert plan.tasks[0].parameters == {
        "target": "example.com",
    }

    assert plan.tasks[0].plugin_id == "whois"