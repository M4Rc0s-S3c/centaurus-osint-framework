from centaurus.planner.planner import Planner
from centaurus.executor.execution import (
    ExecutionPlan,
    ExecutionTask,
)
from centaurus.investigation import Investigation


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

    assert hasattr(
        planner,
        "plan",
    )


def test_planner_returns_execution_plan():
    """
    Planner returns an ExecutionPlan instance.
    """

    planner = Planner()

    investigation = Investigation(
        objective="example.com",
    )

    plan = planner.plan(
        investigation,
    )

    assert isinstance(
        plan,
        ExecutionPlan,
    )


def test_planner_creates_execution_task():
    """
    Planner creates the domain execution tasks supported by the current TFM increment.
    """

    planner = Planner()

    investigation = Investigation(
        objective="example.com",
    )

    plan = planner.plan(
        investigation,
    )

    assert isinstance(
        plan,
        ExecutionPlan,
    )

    assert len(plan.tasks) == 3

    assert all(isinstance(task, ExecutionTask) for task in plan.tasks)


def test_planner_associates_plan_with_investigation():
    """
    Planner associates the ExecutionPlan with the Investigation
    that originated it.
    """

    planner = Planner()

    investigation = Investigation(
        objective="example.com",
    )

    plan = planner.plan(
        investigation,
    )

    assert plan.investigation_id == investigation.id


def test_planner_copies_investigation_objective_to_plan():
    """
    Planner copies the Investigation objective into the
    ExecutionPlan.
    """

    planner = Planner()

    investigation = Investigation(
        objective="example.com",
    )

    plan = planner.plan(
        investigation,
    )

    assert plan.objective == "example.com"


def test_planner_passes_domain_to_whois_execution_task():
    """
    Planner passes the Investigation target to the WHOIS
    execution task using the plugin-specific parameter name.
    """

    planner = Planner()

    investigation = Investigation(
        objective="example.com",
    )

    plan = planner.plan(
        investigation,
    )

    assert len(plan.tasks) == 3

    assert plan.tasks[0].parameters == {
        "domain": "example.com",
    }
    assert plan.tasks[0].plugin_id == "whois"

    assert plan.tasks[1].parameters == {
        "domain": "example.com",
    }
    assert plan.tasks[1].plugin_id == "rdap"

    assert plan.tasks[2].parameters == {
        "domain": "example.com",
    }
    assert plan.tasks[2].plugin_id == "dnsrecon"

def test_planner_uses_rdap_for_ip_target() -> None:
    """IP investigations use RDAP without creating an invalid WHOIS task."""

    planner = Planner()
    investigation = Investigation(
        target="192.0.2.10",
        target_type="IP",
        intent="public_exposure_assessment",
    )

    plan = planner.plan(investigation)

    assert len(plan.tasks) == 1
    assert plan.tasks[0].plugin_id == "rdap"
    assert plan.tasks[0].parameters == {"ip": "192.0.2.10"}


def test_planner_does_not_invent_tool_for_email_target() -> None:
    """EMAIL remains unsupported until its declared tool block is implemented."""

    planner = Planner()
    investigation = Investigation(
        target="analyst@example.com",
        target_type="EMAIL",
        intent="public_exposure_assessment",
    )

    plan = planner.plan(investigation)

    assert plan.tasks == []
