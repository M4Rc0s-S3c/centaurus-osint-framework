"""
Unit tests for the Core component.
"""

from centaurus.core import Core


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

    core.initialize()

    assert planner is core._planner
    assert executor is core._executor
    assert plugin_manager is core._plugin_manager
    assert rule_engine is core._rule_engine
    assert report_manager is core._report_manager
    assert llm_manager is core._llm_manager
