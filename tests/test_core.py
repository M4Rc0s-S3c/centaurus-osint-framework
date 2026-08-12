"""
Unit tests for the Core component.
"""

from datetime import datetime, timezone

import pytest

from centaurus.core import Core
from centaurus.evidence import EvidenceSource, RawObservation
from centaurus.evidence.evidence_manager import EvidenceManager
from centaurus.persistence.filesystem import FilesystemRawObservationStore
from centaurus.executor.execution import ExecutionPlan
from centaurus.investigation import (
    Investigation,
    InvestigationStatus,
)


class FakePlanner:
    """
    Test double for the Planner component.
    """

    def __init__(self, plan: ExecutionPlan) -> None:
        """
        Create a fake Planner with a predefined plan.
        """

        self._plan = plan
        self.received_investigations = []

    def plan(
        self,
        investigation: Investigation,
    ) -> ExecutionPlan:
        """
        Record the Investigation and return the predefined plan.
        """

        self.received_investigations.append(
            investigation,
        )

        return self._plan


class FakeExecutor:
    """
    Test double for the Executor component.
    """

    def __init__(self, result=None) -> None:
        """
        Create a fake Executor with a predefined result.
        """

        if result is None:
            result = {
                "status": "completed",
                "results": [],
            }

        self._result = result
        self.received_plans = []

    def execute(
        self,
        plan: ExecutionPlan,
    ):
        """
        Record the execution plan and return the predefined result.
        """

        self.received_plans.append(
            plan,
        )

        return self._result


class FakeRawObservationStore:
    """
    Test double for the RawObservation persistence boundary.
    """

    def __init__(self) -> None:
        self.persisted = []

    def persist_raw(
        self,
        investigation_id: str,
        observation: RawObservation,
    ):
        self.persisted.append(
            (investigation_id, observation),
        )
        return None


class FailingExecutor:
    """
    Executor that always fails.
    """

    def execute(
        self,
        plan: ExecutionPlan,
    ):
        """
        Simulate an execution failure.
        """

        raise RuntimeError(
            "Execution failed",
        )


def test_core_initial_state():
    """
    Verify the Core initial state.
    """

    core = Core()

    assert core._initialized is False

    assert core._planner is None
    assert core._executor is None
    assert core._plugin_manager is None
    assert core._rule_engine is None
    assert core._report_manager is None
    assert core._llm_manager is None
    assert core._raw_observation_store is None
    assert core._evidence_manager is None


def test_core_initialize_creates_components():
    """
    Verify framework components are created during initialization.
    """

    core = Core()

    core.initialize()

    assert core._initialized is True

    assert core._planner is not None
    assert core._executor is not None
    assert core._plugin_manager is not None
    assert core._rule_engine is not None
    assert core._report_manager is not None
    assert core._llm_manager is not None
    assert core._evidence_manager is not None


def test_core_initialize_is_idempotent():
    """
    Calling initialize() multiple times must not recreate components.
    """

    core = Core()

    core.initialize()

    planner = core._planner
    executor = core._executor
    plugin_manager = core._plugin_manager
    rule_engine = core._rule_engine
    report_manager = core._report_manager
    llm_manager = core._llm_manager
    evidence_manager = core._evidence_manager

    core.initialize()

    assert planner is core._planner
    assert executor is core._executor
    assert plugin_manager is core._plugin_manager
    assert rule_engine is core._rule_engine
    assert report_manager is core._report_manager
    assert llm_manager is core._llm_manager
    assert evidence_manager is core._evidence_manager


def test_core_run_investigation_initializes_framework(tmp_path):
    """
    Running an investigation initializes the framework when needed.
    """

    core = Core(
        raw_observation_store=FilesystemRawObservationStore(tmp_path),
    )

    investigation = Investigation(
        objective="example.com",
    )

    assert core._initialized is False

    core.run_investigation(
        investigation,
    )

    assert core._initialized is True


def test_core_run_investigation_delegates_to_planner():
    """
    Core passes the Investigation to the Planner.
    """

    core = Core()

    plan = ExecutionPlan(
        investigation_id="INV-TEST",
    )

    planner = FakePlanner(
        plan=plan,
    )

    executor = FakeExecutor()

    core._initialized = True
    core._planner = planner
    core._executor = executor

    investigation = Investigation(
        objective="example.com",
    )

    core.run_investigation(
        investigation,
    )

    assert len(
        planner.received_investigations,
    ) == 1

    received = planner.received_investigations[0]

    assert received is investigation

    assert received.objective == "example.com"


def test_core_run_investigation_delegates_plan_to_executor():
    """
    Core passes the plan produced by the Planner to the Executor.
    """

    core = Core()

    plan = ExecutionPlan(
        investigation_id="INV-TEST",
    )

    planner = FakePlanner(
        plan=plan,
    )

    executor = FakeExecutor()

    core._initialized = True
    core._planner = planner
    core._executor = executor

    investigation = Investigation(
        objective="example.com",
    )

    core.run_investigation(
        investigation,
    )

    assert executor.received_plans == [
        plan,
    ]


def test_core_run_investigation_returns_executor_result():
    """
    Core returns the result produced by the Executor.
    """

    core = Core()

    plan = ExecutionPlan(
        investigation_id="INV-TEST",
    )

    expected_result = {
        "status": "completed",
        "results": [
            {
                "plugin": "whois",
                "data": {
                    "domain": "example.com",
                },
            },
        ],
    }

    planner = FakePlanner(
        plan=plan,
    )

    executor = FakeExecutor(
        result=expected_result,
    )

    core._initialized = True
    core._planner = planner
    core._executor = executor

    investigation = Investigation(
        objective="example.com",
    )

    result = core.run_investigation(
        investigation,
    )

    assert result == expected_result

    assert (
        investigation.status
        == InvestigationStatus.COMPLETED
    )

    assert investigation.results == (
        {
            "plugin": "whois",
            "data": {
                "domain": "example.com",
            },
        },
    )


def test_core_persists_raw_observations_with_investigation_id():
    """
    Core persists RawObservations using the Investigation identity.
    """

    core = Core()

    plan = ExecutionPlan(
        investigation_id="INV-TEST",
    )

    observation = RawObservation(
        source=EvidenceSource.WHOIS,
        data={"domain": "example.com"},
        collected_at=datetime.now(timezone.utc),
    )

    planner = FakePlanner(
        plan=plan,
    )

    executor = FakeExecutor(
        result={
            "status": "completed",
            "results": [observation],
        },
    )

    store = FakeRawObservationStore()

    core._initialized = True
    core._planner = planner
    core._executor = executor
    core._raw_observation_store = store

    investigation = Investigation(
        objective="example.com",
    )

    core.run_investigation(
        investigation,
    )

    assert store.persisted == [
        (investigation.id, observation),
    ]



def test_core_normalizes_raw_observation_and_adds_evidence():
    """
    Core coordinates RawObservation normalization through EvidenceManager.
    """

    core = Core()

    plan = ExecutionPlan(
        investigation_id="INV-TEST",
    )

    observation = RawObservation(
        source=EvidenceSource.WHOIS,
        data={
            "domain_name": "EXAMPLE.COM",
            "creation_date": datetime(
                1995,
                8,
                14,
                4,
                0,
                tzinfo=timezone.utc,
            ),
            "name_servers": (
                "NS1.EXAMPLE.COM",
                "NS2.EXAMPLE.COM",
            ),
        },
        collected_at=datetime(
            2026,
            8,
            12,
            10,
            0,
            tzinfo=timezone.utc,
        ),
    )

    planner = FakePlanner(plan)
    executor = FakeExecutor({
        "status": "completed",
        "results": [observation],
    })

    core._initialized = True
    core._planner = planner
    core._executor = executor
    core._evidence_manager = EvidenceManager()

    investigation = Investigation(
        objective="example.com",
    )

    core.run_investigation(investigation)

    assert len(investigation.evidences) == 1
    evidence = investigation.evidences[0]

    assert evidence.source is EvidenceSource.WHOIS
    assert evidence.data == {
        "domain_name": "EXAMPLE.COM",
        "creation_date": "1995-08-14T04:00:00+00:00",
        "name_servers": [
            "NS1.EXAMPLE.COM",
            "NS2.EXAMPLE.COM",
        ],
    }
    assert observation.data["creation_date"].year == 1995
    assert observation.data["name_servers"] == (
        "NS1.EXAMPLE.COM",
        "NS2.EXAMPLE.COM",
    )

def test_core_marks_investigation_completed():
    """
    Core completes the investigation lifecycle.
    """

    core = Core()

    plan = ExecutionPlan(
        investigation_id="INV-TEST",
    )

    planner = FakePlanner(
        plan,
    )

    executor = FakeExecutor(
        {
            "status": "completed",
            "results": [],
        }
    )

    core._initialized = True
    core._planner = planner
    core._executor = executor

    investigation = Investigation(
        objective="example.com",
    )

    core.run_investigation(
        investigation,
    )

    assert (
        investigation.status
        == InvestigationStatus.COMPLETED
    )


def test_core_marks_investigation_failed():
    """
    Core marks the investigation as FAILED when execution fails.
    """

    core = Core()

    planner = FakePlanner(
        ExecutionPlan(
            investigation_id="INV-TEST",
        ),
    )

    executor = FailingExecutor()

    core._initialized = True
    core._planner = planner
    core._executor = executor

    investigation = Investigation(
        objective="example.com",
    )

    with pytest.raises(
        RuntimeError,
        match="Execution failed",
    ):
        core.run_investigation(
            investigation,
        )

    assert (
        investigation.status
        == InvestigationStatus.FAILED
    )
