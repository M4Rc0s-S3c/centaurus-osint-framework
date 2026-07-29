from centaurus.investigation import (
    Investigation,
    InvestigationStatus,
)


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