"""
Planner component.

The Planner is responsible for transforming an investigation
request into an execution plan.
"""


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

    def plan(self, request):
        """
        Build an execution plan from an investigation request.
        """

        raise NotImplementedError
    