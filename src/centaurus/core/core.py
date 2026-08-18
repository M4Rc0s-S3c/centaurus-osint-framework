"""
Core coordination component.

The Core is responsible for coordinating the execution of investigations
and governing the lifecycle of the domain objects participating in them.

At this stage, the Core only builds and owns the main framework
components. Investigation execution will be incorporated during the
Runtime Flow implementation.
"""

import logging

from centaurus.evidence.raw_observation import RawObservation
from centaurus.evidence.evidence_manager import EvidenceManager
from centaurus.investigation import Investigation
from centaurus.persistence.filesystem.raw_observation_store import (
    FilesystemRawObservationStore,
)
from centaurus.persistence.raw_observation_store import RawObservationStore
from centaurus.persistence.evidence_store import EvidenceStore
from centaurus.persistence.report_store import ReportStore
from centaurus.persistence.finding_store import FindingStore
from centaurus.persistence.execution_failure_store import ExecutionFailureStore
from centaurus.persistence.filesystem.evidence_store import FilesystemEvidenceStore
from centaurus.persistence.filesystem.report_store import FilesystemReportStore
from centaurus.persistence.filesystem.finding_store import FilesystemFindingStore
from centaurus.persistence.filesystem.execution_failure_store import (
    FilesystemExecutionFailureStore,
)

from centaurus.planner.planner import Planner
from centaurus.executor.executor import Executor
from centaurus.plugin_manager.plugin_manager import PluginManager

from centaurus.rules.rule import Rule
from centaurus.rules.rule_engine import RuleEngine
from centaurus.report.report_manager import ReportManager
from centaurus.llm.llm_manager import LLMManager
from centaurus.llm.exceptions import LLMError
from centaurus.request import StructuredRequest


logger = logging.getLogger("centaurus.core")


class Core:
    """
    Central coordination component of the CENTAURUS framework.

    Responsibilities
    ----------------
    - Own the lifecycle of the framework components.
    - Coordinate investigation execution.
    - Govern the Investigation aggregate.
    - Mediate communication between framework components.

    The Core does not implement business logic belonging to any
    specialized component.
    """

    def __init__(
        self,
        raw_observation_store: RawObservationStore | None = None,
        evidence_store: EvidenceStore | None = None,
        report_store: ReportStore | None = None,
        finding_store: FindingStore | None = None,
        execution_failure_store: ExecutionFailureStore | None = None,
        llm_manager: LLMManager | None = None,
        rules: tuple[Rule, ...] | None = None,
    ) -> None:
        """
        Create a new Core instance.
        """

        self._initialized = False

        #
        # Framework components
        #

        self._planner = None
        self._executor = None
        self._plugin_manager = None
        self._rule_engine = None
        self._report_manager = None
        self._llm_manager = llm_manager
        self._last_llm_output: str | None = None
        self._last_execution_status: str | None = None
        self._last_execution_failures: tuple = ()
        self._raw_observation_store = raw_observation_store
        self._evidence_store = evidence_store
        self._report_store = report_store
        self._finding_store = finding_store
        self._execution_failure_store = execution_failure_store
        self._evidence_manager = None
        self._rules = rules if rules is not None else ()

    # ==========================================================
    # Public interface
    # ==========================================================

    def initialize(self) -> None:
        """
        Build the framework components.

        This method performs the structural initialization of the
        framework only.

        It does not start investigations or execute plugins.
        """

        if self._initialized:
            return

        self._create_components()

        self._initialized = True

    def submit_request(
        self,
        request: StructuredRequest,
    ) -> Investigation:
        """Create and execute an Investigation from a validated request."""

        if not isinstance(request, StructuredRequest):
            raise TypeError("request must be a StructuredRequest instance")

        investigation = Investigation(
            target=request.target,
            target_type=request.target_type,
            intent=request.intent,
        )
        self.run_investigation(investigation)
        return investigation

    def run_investigation(
        self,
        investigation: Investigation,
    ):
        """
        Coordinate the execution of an investigation.

        The Core delegates planning to the Planner and execution
        to the Executor.

        The Core governs the Investigation aggregate, driving its
        lifecycle through the different execution stages.
        """

        if not self._initialized:
            self.initialize()

        self._last_llm_output = None
        self._last_execution_status = None
        self._last_execution_failures = ()

        investigation.mark_planned()

        plan = self._planner.plan(
            investigation,
        )

        investigation.mark_running()

        try:

            result = self._executor.execute(plan)

            execution_status = result.get("status")
            if execution_status not in {"completed", "partial", "failed"}:
                raise ValueError(
                    f"Unsupported Executor status: {execution_status!r}"
                )

            failures = result.get("failures", [])
            self._last_execution_status = execution_status
            self._last_execution_failures = tuple(failures)
            self._persist_execution_failures(
                investigation.id,
                failures,
            )

            if execution_status == "failed":
                investigation.register_results(
                    result["results"],
                )
                investigation.mark_failed()
                return result

            self._persist_raw_observations(
                investigation.id,
                result["results"],
            )

            self._create_evidence_from_raw_observations(
                result["results"],
                investigation,
            )

            self._evaluate_rules(
                investigation,
            )

            if self._report_manager is None:
                self._create_report_manager()

            report = self._report_manager.generate(
                investigation=investigation,
                findings=investigation.findings,
            )
            investigation.add_report(report)

            if self._report_store is None:
                self._report_store = FilesystemReportStore()
            self._report_store.persist_report(investigation.id, report)

            if self._llm_manager is None:
                self._create_llm_manager()
            try:
                self._last_llm_output = self._llm_manager.generate(report)
            except LLMError as exc:
                # LLM presentation is operational and must not invalidate
                # the completed domain investigation or its persisted Report.
                logger.warning(
                    "LLM presentation failed investigation_id=%s error_type=%s message=%s",
                    investigation.id,
                    type(exc).__name__,
                    exc,
                )
                self._last_llm_output = None

            investigation.register_results(
                result["results"],
            )

            investigation.mark_completed()

            return result

        except Exception:

            investigation.mark_failed()

            raise


    def _create_evidence_from_raw_observations(
        self,
        results: list,
        investigation: Investigation,
    ) -> None:
        """Normalize RawObservations and integrate Evidence into Investigation."""

        if self._evidence_manager is None:
            self._evidence_manager = EvidenceManager()

        for result in results:
            if not isinstance(result, RawObservation):
                continue

            evidence = self._evidence_manager.create_evidence(result)
            investigation.add_evidence(evidence)
            if self._evidence_store is None:
                self._evidence_store = FilesystemEvidenceStore()
            self._evidence_store.persist_evidence(investigation.id, evidence)

    def _evaluate_rules(
        self,
        investigation: Investigation,
    ) -> None:
        """Evaluate configured Rules against normalized Evidence."""

        if not self._rules:
            return

        findings = self._rule_engine.evaluate(
            rules=self._rules,
            evidences=investigation.evidences,
        )

        for finding in findings:
            investigation.add_finding(finding)
            if self._finding_store is None:
                self._finding_store = FilesystemFindingStore()
            self._finding_store.persist_finding(
                investigation.id,
                finding,
            )

    def _persist_execution_failures(
        self,
        investigation_id: str,
        failures: list,
    ) -> None:
        """Persist operational task failures outside the knowledge pipeline."""

        if not failures:
            return

        if self._execution_failure_store is None:
            self._execution_failure_store = FilesystemExecutionFailureStore()

        for failure in failures:
            self._execution_failure_store.persist_failure(
                investigation_id,
                failure,
            )

    def _persist_raw_observations(
        self,
        investigation_id: str,
        results: list,
    ) -> None:
        """Persist RawObservations produced during execution."""

        raw_observations = [
            result
            for result in results
            if isinstance(result, RawObservation)
        ]

        if not raw_observations:
            return

        if self._raw_observation_store is None:
            self._raw_observation_store = FilesystemRawObservationStore()

        for observation in raw_observations:
            self._raw_observation_store.persist_raw(
                investigation_id,
                observation,
            )

    # ==========================================================
    # Internal implementation
    # ==========================================================

    def _create_components(self) -> None:
        """
        Create all framework components.

        Component creation is centralized in the Core to guarantee
        a deterministic framework lifecycle.
        """

        self._create_plugin_manager()
        self._create_evidence_manager()
        self._create_planner()
        self._create_executor()
        self._create_rule_engine()
        self._create_report_manager()
        self._create_llm_manager()

    def _create_evidence_manager(self) -> None:
        """Create the Evidence Manager."""

        self._evidence_manager = EvidenceManager()

    def _create_plugin_manager(self) -> None:
        """
        Create the Plugin Manager.
        """

        self._plugin_manager = PluginManager()

    def _create_planner(self) -> None:
        """
        Create the Planner.
        """

        self._planner = Planner()

    def _create_executor(self) -> None:
        """
        Create the Executor.
        """

        self._executor = Executor(
            plugin_manager=self._plugin_manager,
        )

    def _create_rule_engine(self) -> None:
        """
        Create the Rule Engine.
        """

        self._rule_engine = RuleEngine()

    def _create_report_manager(self) -> None:
        """
        Create the Report Manager.
        """

        self._report_manager = ReportManager()

    def _create_llm_manager(self) -> None:
        """Create the LLM Manager if one was not injected."""

        if self._llm_manager is None:
            self._llm_manager = LLMManager()

    @property
    def last_execution_status(self) -> str | None:
        """Return the latest aggregate Executor status, if one exists."""

        return self._last_execution_status

    @property
    def last_execution_failures(self) -> tuple:
        """Return latest operational task failures as an immutable tuple."""

        return self._last_execution_failures

    @property
    def last_llm_output(self) -> str | None:
        """Return the latest ephemeral LLM presentation, if one exists."""

        return self._last_llm_output
