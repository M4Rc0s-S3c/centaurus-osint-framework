"""
Evidence Manager domain service.
"""

from centaurus.evidence.evidence import Evidence
from centaurus.evidence.raw_observation import RawObservation


class EvidenceManager:
    """
    Domain service responsible for transforming RawObservation
    objects into immutable Evidence Value Objects.
    """

    def create_evidence(
        self,
        raw_observation: RawObservation,
    ) -> Evidence:
        """
        Transform a RawObservation into an immutable Evidence.

        Parameters
        ----------
        raw_observation:
            Normalized observation produced by a plugin.

        Returns
        -------
        Evidence
            Immutable domain representation.

        Raises
        ------
        ValueError
            If the supplied observation is invalid.
        """

        if raw_observation is None:
            raise ValueError("RawObservation cannot be None.")

        if not isinstance(raw_observation, RawObservation):
            raise ValueError("Expected a RawObservation instance.")

        return Evidence(
            source=raw_observation.source,
            data=raw_observation.data,
            collected_at=raw_observation.collected_at,
        )