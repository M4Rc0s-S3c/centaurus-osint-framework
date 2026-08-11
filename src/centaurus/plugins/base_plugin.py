"""
Base contract for every CENTAURUS plugin.
"""

from abc import ABC, abstractmethod

from centaurus.evidence.raw_observation import RawObservation


class BasePlugin(ABC):
    """
    Structural and operational contract implemented by every
    CENTAURUS plugin.
    """

    @abstractmethod
    def execute(
        self,
        parameters: dict,
    ) -> RawObservation:
        """
        Execute the plugin using the supplied task parameters.

        Returns:
            The raw observation produced by the plugin.
        """

        pass