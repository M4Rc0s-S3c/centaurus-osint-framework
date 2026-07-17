"""
Planner component.

The Planner is responsible for transforming an investigation
request into an execution plan.
"""

from centaurus.executor.execution.execution_plan import ExecutionPlan
from centaurus.executor.execution.execution_plan import (
    ExecutionPlan,
    ExecutionTask,
)


class Planner:
    """
    Planner component.

    The Planner only builds execution plans.
    It never executes tasks or interacts directly with external tools.
    """

    def __init__(self) -> None:
        """
        Create a new Planner instance.
        """

        pass

    # ==========================================================
    # Public interface
    # ==========================================================

    def plan(self, request) -> ExecutionPlan:
        """
        Build an execution plan from an investigation request.
        """

        plan = ExecutionPlan()

        task = ExecutionTask()

        plan.tasks.append(task)

        return plan
    