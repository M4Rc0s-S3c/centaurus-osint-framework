"""
Base contract for every CENTAURUS plugin.
"""

from abc import ABC, abstractmethod


class BasePlugin(ABC):
    """
    Structural contract implemented by every CENTAURUS plugin.

    The operational contract (execute signature) is intentionally
    left undefined until the runtime execution model is finalized.
    """

    @abstractmethod
    def execute(self):
        """
        Execute the plugin.
        """

        pass
