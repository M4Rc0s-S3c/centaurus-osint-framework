from centaurus.planner.planner import Planner
from centaurus.executor.execution.execution_plan import (
    ExecutionPlan,
    ExecutionTask,
)


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

    assert hasattr(planner, "plan")


def test_planner_returns_execution_plan():
    """
    Planner returns an ExecutionPlan instance.
    """

    planner = Planner()

    plan = planner.plan(intent=None)

    assert isinstance(plan, ExecutionPlan)

def test_planner_creates_execution_task() -> None:
    """
    Planner creates an execution plan containing one execution task.
    """

    planner = Planner()

    plan = planner.plan(intent=None)

    assert isinstance(plan, ExecutionPlan)
    assert len(plan.tasks) == 1
    assert isinstance(plan.tasks[0], ExecutionTask)
    
