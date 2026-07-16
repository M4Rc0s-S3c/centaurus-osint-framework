from centaurus.planner.planner import Planner


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
    