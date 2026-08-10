"""
Execution domain models.

These classes define the execution plan produced by the Planner
and consumed by the Executor.
"""


class ExecutionPlan:
    """
    Represents an execution plan.

    An execution plan is an ephemeral operational object associated
    with the Investigation that originated it.

    It contains only the information required to coordinate the
    execution of its tasks.
    """

    def __init__(
        self,
        investigation_id: str,
        objective: str | None = None,
    ) -> None:
        """
        Create an execution plan for an Investigation.
        """

        self.investigation_id = investigation_id
        self.objective = objective
        self.tasks = []
        self.metadata = {}
