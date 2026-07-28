"""
Base contract for every CENTAURUS plugin.
"""

from abc import ABC, abstractmethod


class BasePlugin(ABC):
    """
    Structural and operational contract implemented by every
    CENTAURUS plugin.
    """

    @abstractmethod
    def execute(
        self,
        parameters: dict,
    ) -> None:
        """
        Execute the plugin using the supplied task parameters.
        """

        pass
