"""
Core coordination component.

The Core is responsible for coordinating the execution of investigations
and governing the lifecycle of the domain objects participating in them.

At this stage, the Core only builds and owns the main framework
components. Investigation execution will be incorporated during the
Runtime Flow implementation.
"""

from centaurus.investigation import Investigation

from centaurus.planner.planner import Planner
from centaurus.executor.executor import Executor
from centaurus.plugin_manager.plugin_manager import PluginManager

from centaurus.rules.rule_engine import RuleEngine
from centaurus.report.report_manager import ReportManager
from centaurus.llm.llm_manager import LLMManager


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

    def __init__(self) -> None:
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
        self._llm_manager = None

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

        #
        # Investigation lifecycle.
        #

        investigation.mark_planned()

        plan = self._planner.plan(
            investigation,
        )

        investigation.mark_running()

        result = self._executor.execute(plan)

        investigation.register_results(
            result["results"],
        )

        investigation.mark_completed()

        return result

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
        self._create_planner()
        self._create_executor()
        self._create_rule_engine()
        self._create_report_manager()
        self._create_llm_manager()

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
        """
        Create the LLM Manager.
        """

        self._llm_manager = LLMManager()