"""
Execution Task.

Represents a single unit of work within an execution plan.
"""


class ExecutionTask:
    """
    Represent a single planned execution task.

    An ExecutionTask only describes which plugin must be executed
    and the parameters required for its execution.

    It never stores execution state, results, evidence,
    reports or runtime information.
    """

    def __init__(
        self,
        plugin_id: str,
        parameters: dict | None = None,
    ) -> None:
        """
        Create a new execution task.
        """

        self.plugin_id = plugin_id
        self.parameters = parameters or {}