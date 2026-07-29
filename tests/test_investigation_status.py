from centaurus.investigation import (
    InvestigationStatus,
)


def test_investigation_status_contains_created():
    """
    CREATED status exists.
    """

    assert (
        InvestigationStatus.CREATED.value
        == "created"
    )


def test_investigation_status_contains_planned():
    """
    PLANNED status exists.
    """

    assert (
        InvestigationStatus.PLANNED.value
        == "planned"
    )


def test_investigation_status_contains_running():
    """
    RUNNING status exists.
    """

    assert (
        InvestigationStatus.RUNNING.value
        == "running"
    )


def test_investigation_status_contains_completed():
    """
    COMPLETED status exists.
    """

    assert (
        InvestigationStatus.COMPLETED.value
        == "completed"
    )


def test_investigation_status_contains_failed():
    """
    FAILED status exists.
    """

    assert (
        InvestigationStatus.FAILED.value
        == "failed"
    )