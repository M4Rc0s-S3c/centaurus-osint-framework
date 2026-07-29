from centaurus.investigation import (
    Investigation,
    InvestigationStatus,
)

from centaurus.investigation.exceptions import (
    InvalidInvestigationState,
)

import pytest

def test_investigation_can_be_created() -> None:
    """
    An Investigation can be instantiated.
    """

    investigation = Investigation(
        objective="Investigate example.com",
    )

    assert isinstance(
        investigation,
        Investigation,
    )


def test_investigation_generates_identifier() -> None:
    """
    Every Investigation receives an identifier.
    """

    investigation = Investigation(
        objective="Investigate example.com",
    )

    assert investigation.id is not None
    assert investigation.id != ""


def test_investigation_stores_objective() -> None:
    """
    Investigation stores its objective.
    """

    objective = "Investigate example.com"

    investigation = Investigation(
        objective=objective,
    )

    assert investigation.objective == objective


def test_investigation_initial_status() -> None:
    """
    A new Investigation starts in CREATED state.
    """

    investigation = Investigation(
        objective="Investigate example.com",
    )

    assert (
        investigation.status
        is InvestigationStatus.CREATED
    )

def test_investigation_valid_lifecycle() -> None:
    """
    Investigation follows the valid lifecycle.
    """

    investigation = Investigation(
        objective="Investigate example.com",
    )

    investigation.mark_planned()

    assert (
        investigation.status
        is InvestigationStatus.PLANNED
    )

    investigation.mark_running()

    assert (
        investigation.status
        is InvestigationStatus.RUNNING
    )

    investigation.mark_completed()

    assert (
        investigation.status
        is InvestigationStatus.COMPLETED
    )


def test_investigation_can_fail_from_running() -> None:
    """
    Investigation can transition from RUNNING to FAILED.
    """

    investigation = Investigation(
        objective="Investigate example.com",
    )

    investigation.mark_planned()
    investigation.mark_running()
    investigation.mark_failed()

    assert (
        investigation.status
        is InvestigationStatus.FAILED
    )


def test_investigation_cannot_skip_planned() -> None:
    """
    Investigation cannot transition directly from CREATED to RUNNING.
    """

    investigation = Investigation(
        objective="Investigate example.com",
    )

    with pytest.raises(
        InvalidInvestigationState,
    ):
        investigation.mark_running()


def test_investigation_cannot_complete_before_running() -> None:
    """
    Investigation cannot complete before RUNNING.
    """

    investigation = Investigation(
        objective="Investigate example.com",
    )

    with pytest.raises(
        InvalidInvestigationState,
    ):
        investigation.mark_completed()


def test_completed_investigation_cannot_run_again() -> None:
    """
    Completed investigations cannot return to RUNNING.
    """

    investigation = Investigation(
        objective="Investigate example.com",
    )

    investigation.mark_planned()
    investigation.mark_running()
    investigation.mark_completed()

    with pytest.raises(
        InvalidInvestigationState,
    ):
        investigation.mark_running()