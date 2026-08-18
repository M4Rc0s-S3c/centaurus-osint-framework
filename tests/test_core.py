"""
Unit tests for the Core component.
"""

from datetime import datetime, timezone

import pytest

from centaurus.core import Core
from centaurus.evidence import EvidenceSource, RawObservation
from centaurus.plugin_manager.plugin_manager import PluginManager
from centaurus.evidence.evidence_manager import EvidenceManager
from centaurus.persistence.filesystem import FilesystemRawObservationStore
from centaurus.rules.condition import Condition
from centaurus.rules.rule import Rule
from centaurus.rules.rule_engine import RuleEngine
from centaurus.executor.execution import (
    ExecutionFailure,
    ExecutionFailureCategory,
    ExecutionPlan,
)
from centaurus.llm.exceptions import LLMError
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


class FakeEvidenceStore:
    def __init__(self) -> None:
        self.persisted = []

    def persist_evidence(self, investigation_id, evidence):
        self.persisted.append((investigation_id, evidence))
        return None


class FakeReportStore:
    def __init__(self) -> None:
        self.persisted = []

    def persist_report(self, investigation_id, report):
        self.persisted.append((investigation_id, report))
        return None


class FakeFindingStore:
    def __init__(self) -> None:
        self.persisted = []

    def persist_finding(self, investigation_id, finding):
        self.persisted.append((investigation_id, finding))
        return None


class FakeExecutionFailureStore:
    def __init__(self) -> None:
        self.persisted = []

    def persist_failure(self, investigation_id, failure):
        self.persisted.append((investigation_id, failure))
        return None


class FakeLLMManager:
    """Test double for the LLM analyst-assistance boundary."""

    def __init__(self, response="Generated presentation") -> None:
        self.response = response
        self.received = []

    def generate(self, report):
        self.received.append(report)
        return self.response


class FailingLLMManager(FakeLLMManager):
    """Test double that simulates an operational presentation failure."""

    def generate(self, report):
        self.received.append(report)
        raise LLMError("presentation unavailable")


@pytest.fixture(autouse=True)
def isolate_llm_from_core_unit_tests(monkeypatch):
    """Keep Core tests independent from an external Ollama service."""

    monkeypatch.setattr(
        Core,
        "_create_llm_manager",
        lambda self: setattr(self, "_llm_manager", FakeLLMManager()),
    )



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
    assert core._execution_failure_store is None
    assert core._evidence_manager is None
    assert core._rules == ()


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


def test_core_run_investigation_initializes_framework(tmp_path, monkeypatch):
    """
    Running an investigation initializes the framework without external I/O.
    """

    def fake_execute(self, task):
        source = (
            EvidenceSource.RDAP
            if task.plugin_id == "rdap"
            else EvidenceSource.WHOIS
        )
        return RawObservation(
            source=source,
            data={},
            collected_at=datetime(2026, 8, 16, tzinfo=timezone.utc),
        )

    monkeypatch.setattr(PluginManager, "execute", fake_execute)

    core = Core(
        raw_observation_store=FilesystemRawObservationStore(tmp_path),
    )

    investigation = Investigation(
        target="example.com",
        intent="public_exposure_assessment",
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
        target="example.com",
        intent="public_exposure_assessment",
    )

    core.run_investigation(
        investigation,
    )

    assert len(
        planner.received_investigations,
    ) == 1

    received = planner.received_investigations[0]

    assert received is investigation

    assert received.target == "example.com"
    assert received.intent == "public_exposure_assessment"


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
        target="example.com",
        intent="public_exposure_assessment",
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
        target="example.com",
        intent="public_exposure_assessment",
    )

    result = core.run_investigation(
        investigation,
    )

    assert result == expected_result

    assert (
        investigation.status
        == InvestigationStatus.COMPLETED
    )

    assert not hasattr(investigation, "results")


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
        target="example.com",
        intent="public_exposure_assessment",
    )

    core.run_investigation(
        investigation,
    )

    assert store.persisted == [
        (investigation.id, observation),
    ]



def test_core_persists_evidence_and_report_with_investigation_id():
    core = Core()
    plan = ExecutionPlan(investigation_id="INV-TEST")
    observation = RawObservation(
        source=EvidenceSource.WHOIS,
        data={"domain_name": "EXAMPLE.COM"},
        collected_at=datetime.now(timezone.utc),
    )
    evidence_store = FakeEvidenceStore()
    finding_store = FakeFindingStore()
    report_store = FakeReportStore()
    core._initialized = True
    core._planner = FakePlanner(plan)
    core._executor = FakeExecutor({"status": "completed", "results": [observation]})
    core._evidence_manager = EvidenceManager()
    core._evidence_store = evidence_store
    core._finding_store = finding_store
    core._report_store = report_store

    investigation = Investigation(target="example.com", intent="public_exposure_assessment")
    core.run_investigation(investigation)

    assert len(evidence_store.persisted) == 1
    assert evidence_store.persisted[0][0] == investigation.id
    assert len(report_store.persisted) == 1
    assert report_store.persisted[0] == (investigation.id, investigation.report)


def test_core_persists_findings_with_investigation_id() -> None:
    rules = (
        Rule(
            id="RL-001",
            version="1.0",
            name="missing_registrar",
            description="Registrar information is missing.",
            category="registration",
            conditions=(Condition(field="registrar", operator="missing"),),
            conclusion="Registrar information is missing.",
        ),
    )
    observation = RawObservation(
        source=EvidenceSource.WHOIS,
        data={"domain_name": "EXAMPLE.COM", "registrar": None},
        collected_at=datetime(2026, 8, 15, 10, 0, tzinfo=timezone.utc),
    )
    finding_store = FakeFindingStore()
    core = Core()
    core._initialized = True
    core._planner = FakePlanner(ExecutionPlan(investigation_id="INV-TEST"))
    core._executor = FakeExecutor({"status": "completed", "results": [observation]})
    core._evidence_manager = EvidenceManager()
    core._rule_engine = RuleEngine()
    core._rules = rules
    core._finding_store = finding_store

    investigation = Investigation(target="example.com", intent="public_exposure_assessment")
    core.run_investigation(investigation)

    assert len(finding_store.persisted) == 1
    persisted_investigation_id, persisted_finding = finding_store.persisted[0]
    assert persisted_investigation_id == investigation.id
    assert persisted_finding is investigation.findings[0]
    assert persisted_finding.rule.id == "RL-001"
    assert persisted_finding.evidences == investigation.evidences


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
        target="example.com",
        intent="public_exposure_assessment",
    )

    core.run_investigation(investigation)

    assert len(investigation.evidences) == 1
    evidence = investigation.evidences[0]

    assert evidence.source is EvidenceSource.WHOIS
    assert evidence.data["domain_name"] == "EXAMPLE.COM"
    assert evidence.data["creation_date"] == "1995-08-14T04:00:00+00:00"
    assert evidence.data["name_servers"] == [
        "NS1.EXAMPLE.COM",
        "NS2.EXAMPLE.COM",
    ]
    assert evidence.data["registrar"] is None
    assert evidence.data["expiration_date"] is None
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
        target="example.com",
        intent="public_exposure_assessment",
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
        target="example.com",
        intent="public_exposure_assessment",
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


def test_core_evaluates_configured_rules_against_normalized_evidence():
    """
    Core completes the vertical Evidence -> RuleEngine -> Finding flow.
    """

    rules = (
        Rule(
            id="RL-001",
            version="1.0",
            name="missing_registrar",
            description="Registrar information is missing.",
            category="registration",
            conditions=(
                Condition(
                    field="registrar",
                    operator="missing",
                ),
            ),
            conclusion="Registrar information was not observed in normalized registration Evidence.",
        ),
        Rule(
            id="RL-002",
            version="1.0",
            name="missing_name_servers",
            description="Name server information is missing.",
            category="registration",
            conditions=(
                Condition(
                    field="name_servers",
                    operator="missing",
                ),
            ),
            conclusion="Name server information was not observed in normalized registration Evidence.",
        ),
    )

    observation = RawObservation(
        source=EvidenceSource.WHOIS,
        data={
            "domain_name": "EXAMPLE.COM",
            "registrar": None,
            "name_servers": None,
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

    core = Core()
    core._initialized = True
    core._planner = FakePlanner(
        ExecutionPlan(investigation_id="INV-TEST"),
    )
    core._executor = FakeExecutor({
        "status": "completed",
        "results": [observation],
    })
    core._evidence_manager = EvidenceManager()
    core._rule_engine = RuleEngine()
    core._rules = rules

    investigation = Investigation(
        target="example.com",
        intent="public_exposure_assessment",
    )

    core.run_investigation(investigation)

    assert len(investigation.evidences) == 1
    assert len(investigation.findings) == 2

    evidence = investigation.evidences[0]
    findings = investigation.findings

    assert evidence.data["domain_name"] == "EXAMPLE.COM"
    assert {finding.rule.id for finding in findings} == {
        "RL-001",
        "RL-002",
    }
    assert all(finding.evidences == (evidence,) for finding in findings)
    assert observation.data["registrar"] is None
    assert observation.data["name_servers"] is None


def test_core_generates_and_integrates_report_after_findings() -> None:
    """Core integrates a Report after evaluating Findings."""

    rules = (
        Rule(
            id="RL-001",
            version="1.0",
            name="missing_registrar",
            description="Registrar information is missing.",
            category="registration",
            conditions=(Condition(field="registrar", operator="missing"),),
            conclusion="Registrar information is missing.",
        ),
    )
    observation = RawObservation(
        source=EvidenceSource.WHOIS,
        data={
            "domain_name": "EXAMPLE.COM",
            "registrar": None,
        },
        collected_at=datetime(2026, 8, 15, 10, 0, tzinfo=timezone.utc),
    )

    core = Core()
    core._initialized = True
    core._planner = FakePlanner(ExecutionPlan(investigation_id="INV-TEST"))
    core._executor = FakeExecutor({"status": "completed", "results": [observation]})
    core._evidence_manager = EvidenceManager()
    core._rule_engine = RuleEngine()
    core._rules = rules

    investigation = Investigation(target="example.com", intent="public_exposure_assessment")

    core.run_investigation(investigation)

    assert investigation.report is not None
    assert investigation.report.investigation_id == investigation.id
    assert investigation.report.findings == investigation.findings
    assert investigation.status is InvestigationStatus.COMPLETED


def test_core_logs_llm_presentation_failure_without_invalidating_report(monkeypatch) -> None:
    """Operational LLM #2 failure is observable but never invalidates Report."""

    warnings = []
    monkeypatch.setattr(
        "centaurus.core.core.logger.warning",
        lambda message, *args: warnings.append((message, args)),
    )

    report_store = FakeReportStore()
    llm = FailingLLMManager()
    core = Core(report_store=report_store, llm_manager=llm)
    core._initialized = True
    core._planner = FakePlanner(ExecutionPlan(investigation_id="INV-TEST"))
    core._executor = FakeExecutor({"status": "completed", "results": []})
    core._rules = ()

    investigation = Investigation(target="example.com", intent="public_exposure_assessment")
    core.run_investigation(investigation)

    assert investigation.status is InvestigationStatus.COMPLETED
    assert investigation.report is not None
    assert report_store.persisted == [(investigation.id, investigation.report)]
    assert core.last_llm_output is None
    assert len(warnings) == 1
    message, args = warnings[0]
    assert "LLM analyst assistance failed" in message
    assert args[0] == investigation.id
    assert args[1] == "LLMError"
    assert str(args[2]) == "presentation unavailable"


def test_core_generates_empty_report_when_no_findings_exist() -> None:
    """A completed investigation may have a valid empty Report."""

    core = Core()
    core._initialized = True
    core._planner = FakePlanner(ExecutionPlan(investigation_id="INV-TEST"))
    core._executor = FakeExecutor({"status": "completed", "results": []})
    core._rules = ()

    investigation = Investigation(target="example.com", intent="public_exposure_assessment")

    core.run_investigation(investigation)

    assert investigation.findings == ()
    assert investigation.report is not None
    assert investigation.report.findings == ()
    assert investigation.status is InvestigationStatus.COMPLETED


def test_core_submit_request_creates_and_executes_investigation():
    from centaurus.request import PUBLIC_EXPOSURE_ASSESSMENT, StructuredRequest

    plan = ExecutionPlan(investigation_id="INV-PLACEHOLDER")
    planner = FakePlanner(plan=plan)
    executor = FakeExecutor()

    core = Core()
    core._initialized = True
    core._planner = planner
    core._executor = executor
    core._rules = ()

    request = StructuredRequest(
        target="example.com",
        target_type="DOMAIN",
        intent=PUBLIC_EXPOSURE_ASSESSMENT,
    )

    investigation = core.submit_request(request)

    assert isinstance(investigation, Investigation)
    assert investigation.target == "example.com"
    assert investigation.target_type == "DOMAIN"
    assert investigation.intent == PUBLIC_EXPOSURE_ASSESSMENT
    assert investigation.status is InvestigationStatus.COMPLETED
    assert planner.received_investigations == [investigation]


def test_core_submit_request_rejects_unstructured_input():
    core = Core()

    with pytest.raises(TypeError, match="StructuredRequest"):
        core.submit_request("investiga example.com")  # type: ignore[arg-type]


def _execution_failure(
    plugin_id: str = "crtsh",
    task_index: int = 6,
) -> ExecutionFailure:
    return ExecutionFailure(
        task_index=task_index,
        plugin_id=plugin_id,
        parameters={"domain": "example.com"},
        category=ExecutionFailureCategory.TIMEOUT,
        error_type="ReadTimeout",
        message="timed out",
        occurred_at=datetime(2026, 8, 18, 8, 0, tzinfo=timezone.utc),
    )


def test_core_completes_partial_investigation_and_persists_operational_failure() -> None:
    observation = RawObservation(
        source=EvidenceSource.WHOIS,
        data={"domain_name": "EXAMPLE.COM"},
        collected_at=datetime(2026, 8, 18, 8, 0, tzinfo=timezone.utc),
    )
    failure = _execution_failure()
    failure_store = FakeExecutionFailureStore()
    raw_store = FakeRawObservationStore()
    evidence_store = FakeEvidenceStore()
    report_store = FakeReportStore()

    core = Core(
        raw_observation_store=raw_store,
        evidence_store=evidence_store,
        report_store=report_store,
        execution_failure_store=failure_store,
    )
    core._initialized = True
    core._planner = FakePlanner(ExecutionPlan(investigation_id="INV-TEST"))
    core._executor = FakeExecutor({
        "status": "partial",
        "results": [observation],
        "failures": [failure],
    })
    core._evidence_manager = EvidenceManager()

    investigation = Investigation(target="example.com", intent="public_exposure_assessment")
    result = core.run_investigation(investigation)

    assert result["status"] == "partial"
    assert investigation.status is InvestigationStatus.COMPLETED
    assert not hasattr(investigation, "results")
    assert len(investigation.evidences) == 1
    assert investigation.report is not None
    assert failure_store.persisted == [(investigation.id, failure)]
    assert raw_store.persisted == [(investigation.id, observation)]
    assert all(item is not failure for item in investigation.evidences)
    assert all(item is not failure for item in investigation.findings)


def test_core_marks_investigation_failed_when_all_planned_tools_fail() -> None:
    failure = _execution_failure("whois", 1)
    failure_store = FakeExecutionFailureStore()
    report_store = FakeReportStore()
    llm = FakeLLMManager()

    core = Core(
        report_store=report_store,
        execution_failure_store=failure_store,
        llm_manager=llm,
    )
    core._initialized = True
    core._planner = FakePlanner(ExecutionPlan(investigation_id="INV-TEST"))
    core._executor = FakeExecutor({
        "status": "failed",
        "results": [],
        "failures": [failure],
    })

    investigation = Investigation(target="example.com", intent="public_exposure_assessment")
    result = core.run_investigation(investigation)

    assert result["status"] == "failed"
    assert investigation.status is InvestigationStatus.FAILED
    assert not hasattr(investigation, "results")
    assert investigation.evidences == ()
    assert investigation.findings == ()
    assert investigation.report is None
    assert failure_store.persisted == [(investigation.id, failure)]
    assert report_store.persisted == []
    assert llm.received == []
    assert core.last_llm_output is None


def test_core_rejects_unknown_executor_status_as_framework_failure() -> None:
    core = Core()
    core._initialized = True
    core._planner = FakePlanner(ExecutionPlan(investigation_id="INV-TEST"))
    core._executor = FakeExecutor({
        "status": "mystery",
        "results": [],
        "failures": [],
    })

    investigation = Investigation(target="example.com", intent="public_exposure_assessment")

    with pytest.raises(ValueError, match="Unsupported Executor status"):
        core.run_investigation(investigation)

    assert investigation.status is InvestigationStatus.FAILED


def test_core_exposes_latest_executor_status_and_failures():
    failure = ExecutionFailure(
        task_index=1,
        plugin_id="whois",
        parameters={"domain": "example.com"},
        category=ExecutionFailureCategory.TIMEOUT,
        error_type="TimeoutError",
        message="timed out",
        occurred_at=datetime(2026, 8, 18, tzinfo=timezone.utc),
    )
    core = Core(execution_failure_store=FakeExecutionFailureStore())
    plan = ExecutionPlan(investigation_id="INV-TEST")
    core._initialized = True
    core._planner = FakePlanner(plan=plan)
    core._executor = FakeExecutor(
        result={"status": "partial", "results": [], "failures": [failure]}
    )

    investigation = Investigation(target="example.com", intent="public_exposure_assessment")
    core.run_investigation(investigation)

    assert core.last_execution_status == "partial"
    assert core.last_execution_failures == (failure,)


def test_core_resets_latest_execution_state_before_new_run():
    core = Core()
    core._last_execution_status = "partial"
    core._last_execution_failures = ("old",)
    plan = ExecutionPlan(investigation_id="INV-TEST")
    core._initialized = True
    core._planner = FakePlanner(plan=plan)
    core._executor = FailingExecutor()

    investigation = Investigation(target="example.com", intent="public_exposure_assessment")

    with pytest.raises(RuntimeError, match="Execution failed"):
        core.run_investigation(investigation)

    assert core.last_execution_status is None
    assert core.last_execution_failures == ()
