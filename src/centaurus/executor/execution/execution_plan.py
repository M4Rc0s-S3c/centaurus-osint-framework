"""
Execution domain models.

These classes define the execution plan produced by the Planner
and consumed by the Executor.
"""


class ExecutionTask:
    """
    Represents a single executable task.
    """

    def __init__(self) -> None:
        """
        Create an empty execution task.
        """

        self.id = None
        self.plugin = None
        self.parameters = None


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

        