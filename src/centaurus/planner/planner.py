"""
Planner component.

The Planner is responsible for transforming an investigation
into an execution plan.
"""

from centaurus.executor.execution import (
    ExecutionPlan,
    ExecutionTask,
)
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

        #
        # Temporary planning.
        #
        # A fixed execution plan is currently produced so the
        # runtime execution flow can be exercised end-to-end.
        #
        # Future versions will build the execution plan from the
        # Investigation contents.
        #

        if investigation.target_type == "DOMAIN":
            plan.tasks.append(
                ExecutionTask(
                    plugin_id="whois",
                    parameters={
                        "domain": investigation.target,
                    },
                )
            )
            plan.tasks.append(
                ExecutionTask(
                    plugin_id="rdap",
                    parameters={
                        "domain": investigation.target,
                    },
                )
            )

        elif investigation.target_type == "IP":
            plan.tasks.append(
                ExecutionTask(
                    plugin_id="rdap",
                    parameters={
                        "ip": investigation.target,
                    },
                )
            )


        return plan