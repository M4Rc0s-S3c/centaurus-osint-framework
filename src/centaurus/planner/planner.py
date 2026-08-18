"""
Planner component.

The Planner is responsible for transforming an investigation
into an execution plan.
"""

from centaurus.capabilities import get_operational_target_capability
from centaurus.executor.execution import ExecutionPlan
from centaurus.investigation import Investigation


class Planner:
    """
    Planner component.

    The Planner builds execution plans from Investigation
    aggregates.

    It never executes tasks, accesses plugins or performs
    external operations.
    """

    # ==========================================================
    # Public interface
    # ==========================================================

    def plan(
        self,
        investigation: Investigation,
    ) -> ExecutionPlan:
        """
        Build an execution plan from an Investigation.
        """

        plan = ExecutionPlan(
            investigation_id=investigation.id,
            objective=investigation.objective,
        )

        capability = get_operational_target_capability(
            investigation.target_type
        )
        plan.tasks.extend(
            template.build(investigation.target)
            for template in capability.tasks
        )

        return plan