"""
Domain exceptions for the Investigation aggregate.
"""


class InvalidInvestigationState(Exception):
    """
    Raised when an invalid investigation state transition is attempted.
    """