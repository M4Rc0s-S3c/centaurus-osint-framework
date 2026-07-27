"""
Execution domain models.

These classes define the execution plan produced by the Planner
and consumed by the Executor.
"""


class ExecutionPlan:
    """
    Represents an execution plan.

    An execution plan contains one or more execution tasks.
    """

    def __init__(self) -> None:
        """
        Create an empty execution plan.
        """

        self.objective = None
        self.tasks = []
        self.metadata = {}
