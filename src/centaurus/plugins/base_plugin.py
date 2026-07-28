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
    ) -> dict:
        """
        Execute the plugin using the supplied task parameters.

        Returns:
            A structured dictionary containing the result
            produced by the plugin.
        """

        pass