"""
Planner component.

The Planner is responsible for transforming an investigation
intent into an execution plan.
"""

from centaurus.executor.execution import (
    ExecutionPlan,
    ExecutionTask,
)


class Planner:
    """
    Planner component.

    The Planner builds execution plans from investigation intents.

    It never executes tasks, accesses plugins or performs
    external operations.
    """

    # ==========================================================
    # Public interface
    # ==========================================================

    def plan(self, intent) -> ExecutionPlan:
        """
        Build an execution plan from an investigation intent.
        """

        plan = ExecutionPlan()

        #
        # Temporary planning.
        # Future versions will generate one or more ExecutionTask
        # objects according to the investigation intent.
        #

        task = ExecutionTask(
            plugin_id="whois",
            parameters={},
        )

        plan.tasks.append(task)

        return plan
    